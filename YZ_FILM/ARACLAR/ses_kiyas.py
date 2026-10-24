"""SES KIYAS — ses dönüştürme motoru kıyası (TASARIM Ö0-c, §2.2 karar 4, §1.3 A10c "seri başında ses_kiyas"; [SM2] SB3, §4.7.2 S1.11–S1.12)
ve KUR2 kurulum planı (D-37: KUR2 = yalnız Ö0-c'de kazanan ses dönüştürme motoru, tek ayrı ortam).

Kullanım:
  python ses_kiyas.py --kiyas --film F [--klipler <klasör>] [--karakter <id>] [--motorlar openvoice,chatterbox] [--saglayici sahte]
        Arşiv Veo konuşma klipleri (B2/B3; FILM_AYAR yollar.arsiv_klipler ya da --klipler; klip başına <klip>.json {metin, teslim})
        her motorla karakterin seçilmiş evren sesine çevrilir; ölçüler: hedef merkez benzerliği (≥ 0,70), zarf gecikmesi (≤ 20 ms),
        ASR WER artışı (≤ 0,05) (S1.11), F0 izi, fısıltı ve bağırma başarısı (her biri ≥ 4 replik zorunlu; yoksa BAYRAK), doğallık
        (lisanslı MOS tahmincisi ve/veya dinleyici kör ikili; ikisi de yoksa ÖLÇÜLEMEDİ BAYRAK + örnekler izle-dinle paketine).
        "TTS + süreye sığdırma" çıta olarak tabloya girer (ana yol olamaz); `tts_dudak` (MuseTalk) kuruluysa S1.12 ile girer.
        → _RAPOR/S1b_motor_kiyas.json, _SES/MOTOR_SIRASI.json (sıra, tts_dudak açık/kapalı, ana yol veo_donustur | B), _SES/MOTOR_ORNEKLERI.json
  python ses_kiyas.py --kur2-plan [--json]     KUR2 kurulum planı (kurulum.py çağırır: ses_kiyas.kur2_plani()); hiçbir şey kurmaz
Kodda: kur2_plani(o0c=None, motor=None) → {kur, motor, python, venv, adimlar[], lisans, deneme_kipi, neden}
Çıkış kodları: 0 rapor/plan yazıldı · 1 girdi yok (klip, karakter sesi) · 4 kullanım.
"""
import os, sys, re, json, glob, math
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak
import ses_ortak as so

SURUM = "ses_kiyas 1.0"
# Motor kurulum bilgisi (bellekten; kurulumda doğrulanır — paket adları ve Python sürümleri LISANSLAR.json/kurulum raporuna yazılır)
MOTORLAR = {
    "openvoice": {"lisans_bileseni": "openvoice_v2", "python": "3.10", "pip": ["git+https://github.com/myshell-ai/OpenVoice.git"],
                  "not": "geçişli bağımlılıkta AGPL'li whisper-timestamped bulunabilir: bulunursa o kod yolu kapatılır (D-36)"},
    "chatterbox": {"lisans_bileseni": "chatterbox", "python": "3.11", "pip": ["chatterbox-tts"], "not": "çıktıya görünmez filigran gömer"},
    "rvc": {"lisans_bileseni": "rvc", "python": "3.12", "pip": ["rvc-python"],
            "not": "yalnız ElevenLabs/AI84 koşulları TTS çıktısıyla eğitime izin veriyorsa (§2.2 karar 4)"},
}


def log(*a): print(*a, flush=True)


# --- KUR2 ------------------------------------------------------------------------------------------------------------
def _o0c():
    try: v = ortak.yollar()["veri_kok"]
    except ortak.YolYok: return None
    return ortak.json_oku(os.path.join(v, "BILGI", "OLCUM0", "O0c.json"), None)


def kur2_plani(o0c=None, motor=None):
    """KUR2 planı: Ö0-c kazananı (ya da verilen motor) için tek ayrı ortam. Kurmaz; kurulum.py uygular ve kartına yazar."""
    from olcum import ses as O
    o = o0c if o0c is not None else _o0c()
    if motor is None and isinstance(o, dict):
        sira = o.get("ses_donustur_sira") or o.get("sira") or ([o["kazanan"]] if o.get("kazanan") else [])
        motor = sira[0] if sira else None
    if not motor:
        return {"kur": False, "kademe": "KUR2", "neden": "Ö0-c ölçülmedi ya da eşiği geçen motor yok (O0c.json); KUR2 kurulmaz, "
                                                      "ana yol kararı §2.2 B planına göre verilir"}
    if motor not in MOTORLAR: return {"kur": False, "kademe": "KUR2", "motor": motor, "neden": f"bilinmeyen motor: {motor}"}
    M = MOTORLAR[motor]; lis = O.lisans(M["lisans_bileseni"])
    agpl = [g for g in lis.get("gecisli") or [] if "agpl" in json.dumps(g, ensure_ascii=False).lower()]
    try: y = ortak.yollar()
    except ortak.YolYok: y = {}
    venv = os.path.join(y.get("onbellek") or os.path.join(os.path.expanduser("~"), ".cache", "yz_film"), "venv", f"ses_donustur_{motor}")
    win = os.name == "nt"
    py_anahtar = {"3.12": "py312", "3.11": "py311"}.get(M["python"])
    py = ((y.get("python") or {}).get(py_anahtar) if py_anahtar else (y.get("python") or {}).get("ana")) or (
        ["py", f"-{M['python']}"] if win else [f"python{M['python']}"])
    py = py if isinstance(py, list) else [py]
    vpy = os.path.join(venv, "Scripts" if win else "bin", "python.exe" if win else "python")
    dogrulanmis = lis.get("dogrulama") not in (None, "bilinmiyor")
    adim = [{"ne": "ayrı sanal ortam", "komut": py + ["-m", "venv", venv]},
            {"ne": "pip güncelle", "komut": [vpy, "-m", "pip", "install", "--upgrade", "pip"]},
            {"ne": f"{motor} paketleri", "komut": [vpy, "-m", "pip", "install"] + M["pip"], "dogrulanacak": True},
            {"ne": "YOLLAR.json ortamlar.ses_donustur", "yollar": {"ortamlar.ses_donustur": vpy}},
            {"ne": "model ağırlıkları bir kez indirilir, sonra HF_HUB_OFFLINE=1", "ortam_degiskeni": {"HF_HUB_OFFLINE": "1"}}]
    if O.lisans_dogrulandi("mos_tahmincisi", ticari=False):
        adim.append({"ne": "MOS tahmincisi (lisansı doğrulandı)", "komut": [vpy, "-m", "pip", "install", "utmos"], "dogrulanacak": True})
    return {"kur": True, "kademe": "KUR2", "motor": motor, "python": M["python"], "venv": venv, "python_yolu": vpy, "adimlar": adim,
            "lisans": {"bilesen": M["lisans_bileseni"], "dogrulama": lis.get("dogrulama"), "kod": lis.get("kod_lisansi"),
                       "agirlik": lis.get("agirlik_lisansi"), "agpl_gecisli": agpl},
            "deneme_kipi": not dogrulanmis, "not": M["not"],
            "neden": None if dogrulanmis else "lisans 'bilinmiyor': kurulum yalnız --deneme kipinde (D-36)",
            "kapali_yol": "AGPL'li geçişli bağımlılık bulundu: o kod yolu kapalı" if agpl else None}


# --- kıyas -----------------------------------------------------------------------------------------------------------
def klip_seti(film, klasor):
    if not klasor:
        klasor = ((so.ayar(film).get("yollar") or {}).get("arsiv_klipler")) or os.path.join(film, "_SES", "KIYAS_KLIPLERI")
    out = []
    for p in sorted(glob.glob(os.path.join(klasor, "*.wav")) + glob.glob(os.path.join(klasor, "*.mp4"))):
        j = ortak.json_oku(os.path.splitext(p)[0] + ".json", None) or ortak.json_oku(p + ".sahte.json", None) or {}
        out.append({"klip": p, "metin": j.get("metin") or "", "teslim": so.teslim_sinifi(j.get("teslim"))})
    return out, klasor


def hedef_ses(film, kid):
    from olcum import ses as O
    _, asama = so.evren_ses_yolu(film, kid); k = ortak.json_oku(asama, None)
    if not k:
        kal, _ = so.evren_ses_yolu(film, kid); k = ortak.json_oku(kal, None) if kal else None
    if not k: return None
    vid = (k.get("secim") or {}).get("voice_id"); mer = (k.get("olcum") or {}).get("merkez")
    refs = sorted(glob.glob(os.path.join(film, "SESLER", "ses_secim", "okuma", f"{kid}_{vid}_*.wav")))
    if mer is None and refs:
        g = [O.gomme(O.oku(r)[0]) for r in refs]; mer = [float(sum(v) / len(v)) for v in zip(*g)]
    return {"voice_id": vid, "merkez": mer, "referanslar": refs, "f0": (k.get("olcum") or {}).get("f0_medyan_hz")}


def kiyas(film, klasor=None, kid=None, motorlar=None, saglayici=None):
    from olcum import ses as O
    if kid is None:
        ana = [k for k, v in (so.hikaye(film).get("karakterler") or {}).items() if (v or {}).get("rol") in ("kahraman", "ana")]
        kid = (ana or list((so.hikaye(film).get("karakterler") or {})) or [None])[0]
    H = hedef_ses(film, kid) if kid else None
    if not H or not H.get("merkez"): log(f"!! {kid}: seçilmiş ses (evren ses.json) ya da referans yok; önce ses_sec --sec"); return so.HATA, None
    kl, klasor = klip_seti(film, klasor)
    if not kl: log(f"!! kıyas klibi yok: {klasor}"); return so.HATA, None
    sahte = so.sahte_mi(film, saglayici)
    adlar = motorlar or (["sahte"] if sahte else so.zincir_adlari("ses_donustur", film))
    asr = (so.zincir("asr", film, saglayici_=saglayici) or [None])[0]; din = (so.zincir("dinleyici", film, saglayici_=saglayici) or [None])[0]
    olc, tablo, ornek = [], {}, {}
    ozel = {t: sum(1 for k in kl if k["teslim"] == t) for t in ("fisilti", "bagirma")}
    enaz = int(so.esik("motor_kiyas_ozel_min"))
    olc.append(so.m("S1.11_set", "GEC" if (len(kl) >= 20 and all(v >= enaz for v in ozel.values())) else "BAYRAK",
                    olcu={"klip": len(kl), **ozel}, esik=f"≥ 20 replik; fısıltı ve bağırma her biri ≥ {enaz}"))
    for ad in adlar:
        s = so.saglayici(ad)
        if s is None or "ses_donustur" not in getattr(s, "turler", ()):
            tablo[ad] = {"durum": "kurulu değil"}; continue
        ok, neden = s.hazir()
        if not ok: tablo[ad] = {"durum": f"hazır değil: {neden}"}; continue
        sat = []
        for k in kl:
            out = os.path.join(film, "SESLER", "kiyas", ad, os.path.splitext(os.path.basename(k["klip"]))[0] + ".wav")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            x, _ = O.oku(k["klip"]); f_kay = O.f0(x)["medyan_hz"]
            f0_yt = round(O.yarim_ton(f_kay, H["f0"]) or 0.0, 2) if (f_kay and H.get("f0")) else 0.0
            try: s.ses_donustur(film, k["klip"], kid, out, f0_yt, hedef_ses=H["voice_id"])
            except Exception as e: sat.append({"klip": k["klip"], "hata": str(e)[:80]}); continue
            y, _ = O.oku(out)
            w0 = O.wer(k["metin"], asr.asr(film, k["klip"])["metin"]) if (asr and k["metin"]) else None
            w1 = O.wer(k["metin"], asr.asr(film, out)["metin"]) if (asr and k["metin"]) else None
            mos = O.mos_tahmin(out)
            sat.append({"klip": os.path.basename(k["klip"]), "teslim": k["teslim"], "benzerlik": round(O.benzerlik(O.gomme(y), H["merkez"]) or 0, 3),
                        "gecikme_ms": O.zarf_gecikme_ms(x, y), "wer_artis": (round(w1 - w0, 3) if (w0 is not None and w1 is not None) else None),
                        "f0_iz": O.benzerlik(O.f0_dizisi(x)[:500], O.f0_dizisi(y)[:500]) if len(O.f0_dizisi(x)) else None,
                        "mos": mos.get("mos"), "cikti": os.path.relpath(out, film)})
            if k["teslim"] in ("fisilti", "bagirma"): ornek.setdefault(ad, []).append(os.path.relpath(out, film))
        iyi = [r for r in sat if "hata" not in r]
        if not iyi: tablo[ad] = {"durum": "çıktı yok", "satirlar": sat}; continue
        med = lambda v: sorted(v)[len(v) // 2] if v else None
        bz = med([r["benzerlik"] for r in iyi]); gc = max([abs(r["gecikme_ms"]) for r in iyi if r["gecikme_ms"] is not None] or [None]) \
            if any(r["gecikme_ms"] is not None for r in iyi) else None
        wa = [r["wer_artis"] for r in iyi if r["wer_artis"] is not None]; wa = sum(wa) / len(wa) if wa else None
        mos = [r["mos"] for r in iyi if r["mos"] is not None]
        ozel_ok = {t: (sum(1 for r in iyi if r["teslim"] == t and r["benzerlik"] >= so.esik("ses_donusum_benzerlik_min")) /
                       max(1, sum(1 for r in iyi if r["teslim"] == t))) for t in ("fisilti", "bagirma")}
        gec = (bz is not None and bz >= so.esik("ses_donusum_benzerlik_min")) and (gc is not None and gc <= so.esik("ses_donusum_zarf_gecikme_max_ms")) \
            and (wa is None or wa <= so.esik("ses_donusum_wer_artis_max"))
        tablo[ad] = {"durum": "olculdu", "benzerlik_medyan": bz, "gecikme_max_ms": gc, "wer_artis_ort": None if wa is None else round(wa, 3),
                     "ozel_basari": ozel_ok, "mos_ort": round(sum(mos) / len(mos), 2) if mos else None, "s1_11": gec, "satirlar": sat}
        olc.append(so.m("S1.11", "GEC" if gec else "HATA", birim=ad, olcu={k: tablo[ad][k] for k in ("benzerlik_medyan", "gecikme_max_ms", "wer_artis_ort")},
                        esik="benzerlik ≥ 0,70; gecikme ≤ 20 ms; WER artışı ≤ 0,05"))
        if mos:
            olc.append(so.m("S1.dogallik", "GEC" if tablo[ad]["mos_ort"] >= so.esik("ses_dogallik_mos_min") else "BAYRAK", birim=ad,
                            olcu=tablo[ad]["mos_ort"], esik=f"MOS ≥ {so.esik('ses_dogallik_mos_min')}"))
        else:
            olc.append(so.m("S1.dogallik", "OLCULEMEDI", birim=ad, olcu="MOS lisansı doğrulanmadı / dinleyici yok" if din is None else "dinleyici kör ikili: P1",
                            esik="doğallık ölçüsü", neden="seçim 'ölçülemedi' BAYRAK'ıyla; fısıltı/bağırma örnekleri izle-dinle paketine"))
    tablo["tts_sigdirma"] = {"durum": "cita", "not": "TTS + süreye sığdırma: dudak uyumu zayıf (B2); ana yol olamaz"}
    mt = so.saglayici("musetalk"); dudak = bool(mt and getattr(mt, "hazir", lambda: (False, ""))()[0])
    tablo["tts_dudak"] = {"durum": "acik" if dudak else "kapali", "not": "S1.12 (V2 kimlik + S3) video sonrası dilimde ölçülür"}
    sira = sorted([a for a, t in tablo.items() if t.get("s1_11")], key=lambda a: -(tablo[a]["benzerlik_medyan"] - 2 * (tablo[a]["wer_artis_ort"] or 0)
                                                                                - (tablo[a]["gecikme_max_ms"] or 0) / 100 + (tablo[a]["mos_ort"] or 0) / 10))
    dogallik_yok = all(tablo[a].get("mos_ort") is None for a in sira) if sira else True
    karar = {"_surum": 1, "sira": sira, "tts_dudak": "acik" if dudak else "kapali", "ana_yol": "veo_donustur" if sira else "B",
             "dogallik_olculemedi": dogallik_yok, "karakter": kid, "zaman": so.simdi()}
    ortak.atomik_yaz(os.path.join(film, "_SES", "MOTOR_SIRASI.json"), karar)
    ortak.atomik_yaz(os.path.join(film, "_SES", "MOTOR_ORNEKLERI.json"), {"_surum": 1, "ornekler": ornek, "not": "izle-dinle bilgi paketi (D-24)"})
    if not sira: olc.append(so.m("S1.11_karar", "BAYRAK", olcu="eşiği geçen motor yok: §2.2 B planı (tts_dudak); karar defterine 'ana yol B'",
                                 esik="en az bir motor S1.11"))
    return so.BITTI, so.rapor(film, "S1b", "motor_kiyas", olc, asama="A10c", birimler=[a for a in adlar], arac=SURUM,
                              ek={"tablo": tablo, "karar": karar})


def main(argv):
    if "--kur2-plan" in argv:
        p = kur2_plani(); print(json.dumps(p, ensure_ascii=False, indent=1) if "--json" in argv else
                               (f"KUR2: {p.get('motor')} · {'kur' if p['kur'] else 'kurulmaz'} · {p.get('neden') or ''}")); return 0
    if "--kiyas" not in argv: print(__doc__); return 4
    try: film = so.film_coz(so.arg(argv, "--film"))
    except (ValueError, ortak.YolYok) as e: log(f"!! {e}"); return 4
    mot = so.arg(argv, "--motorlar"); mot = mot.split(",") if mot else None
    kod, r = kiyas(film, so.arg(argv, "--klipler"), so.arg(argv, "--karakter"), mot, so.arg(argv, "--saglayici"))
    if r: log(f"S1b motor kıyası → {r[1]['sonuc']} · sıra {r[1]['karar']['sira']} ({os.path.relpath(r[0], film)})")
    return kod


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
