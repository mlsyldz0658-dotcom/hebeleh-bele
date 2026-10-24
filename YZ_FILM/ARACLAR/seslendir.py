"""SESLENDİR — replik sesi yönlendiricisi (TASARIM §6.6, §2.2, §1.3 A12/A14a/A15; [SM2] §4.2 SB5, §4.5.7, §4.6.1, §4.7.3 S2.12–S2.14).

Kullanım (film.py görevi):
  python seslendir.py --animatik --film F [--saglayici sahte]
        Bütün replikler SEÇİLMİŞ SON SESLE okunur (evren ses.json / SAHNELER karakterler.<id>.ses). Önbellekli: değişmeyen replik ikinci
        kez ücretlenmez (sonraki turlarda yalnız değişenler). Replik başına: gerçek süre, kelime zamanları (sağlayıcı ya da ASR hizalama;
        yoksa harf oranıyla tahmini + BAYRAK), örnek tepe (S2.14), seviye sınıfı (teslim → fısıltı/yumuşak/normal/bağırma) hedefine TEK
        doğrusal kazanç (tepeye göre ölçekleme yok; S4.1 T1), süre kapısı S2.13 (süre + 0,4 + 0,25·(cümle−1) + 0,5 ≤ planın penceresi +
        L taşması). Sığmayan replik HATA + KUYRUK/YENIDEN_YAZ (yönetmen: böl, ekran dışına taşı ya da 10 sn klip).
        → SESLER/tts/<R>_<özet>.wav, SESLER/diyalog.json v2 (+ eski okuyucular için _eski), _RAPOR/S2_ANIMATIK.json
  python seslendir.py --parti N [--kesit] --film F
        Video sonrası yönlendirme: yol tts → animatikteki dosya (önbellekten, 0 kredi; metin değiştiyse yeniden); yol veo_donustur/veo_ham →
        ses_donustur.py (video sonrası ses dilimi; yoksa 4 ORTAM). Sessiz geri dönüş YOK: TTS başarısızsa replik HATA'dır, Flow sesine düşülmez.
  python seslendir.py <film_klasoru>     (v1 SAHNELER) eski yol: seslendir_v1.py (bilinen kusurlarıyla; yalnız eski filmler)
Kredi: kredili sağlayıcıda önce BUTK (kredi.py; AI84 film dilimi) toplam önbelleksiz harf için; her gönderimden ÖNCE kredi defterine
  gönderim satırı. Kesilen çalıştırmadan sonra gönderilmiş ama dosyası olmayan replikte önce sağlayıcı önbelleği toplanır; bulunamazsa
  'kayip' yazılır ve yalnız bir kez yeniden gönderilir (kör yeniden gönderim yok).
Çıkış kodları: 0 rapor yazıldı (S2 sonucu raporda) · 1 girdi yok/bozuk · 4 ORTAM (hazır TTS yok, ses_donustur yok) · 5 BÜTÇE ·
               7 KISIT (sağlayıcı geçilemez kısıt).
"""
import os, sys, json, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak
import ses_ortak as so

SURUM = "seslendir 2.0"
SR = so.SR


def log(*a): print(*a, flush=True)


# --- diyalog.json v2 -------------------------------------------------------------------------------------------------
def diyalog_oku(film):
    d = ortak.json_oku(os.path.join(film, "SESLER", "diyalog.json"), None)
    if not isinstance(d, dict) or int(d.get("surum") or 1) < 2: d = {"surum": 2, "ornekleme_hz": SR, "replikler": {}, "_eski": {}}
    d.setdefault("replikler", {}); d.setdefault("_eski", {})
    return d


def diyalog_yaz(film, d):
    d["surum"], d["ornekleme_hz"] = 2, SR
    eski = {}
    for rid, r in d["replikler"].items():
        if not r.get("dosya") or r.get("kaynak_plan") is None: continue
        eski.setdefault(str(r["kaynak_plan"]), {"ortam": None, "cumleler": []})["cumleler"].append(
            {"dosya": r["dosya"], "bas": (r.get("klip_zamani") or {}).get("bas", 0.0), "sure": (r.get("tts") or {}).get("sure_sn"),
             "en": r.get("duyulan_metin") or r.get("senaryo_metin"), "tr": " ".join(r.get("tr") or []), "kaynak": r.get("yol_gercek") or "tts"})
    d["_eski"] = eski                                   # capcut_film/izleme_paketi eski okuyucuları için bir sürüm boyunca
    ortak.atomik_yaz(os.path.join(film, "SESLER", "diyalog.json"), d)


# --- seviye (S4.1, T1) -----------------------------------------------------------------------------------------------
def seviye_hedefi(r):
    sinif = r.get("seviye_ozel") or so.teslim_sinifi(r.get("teslim"))
    return sinif, float(so.esik("diyalog_lufs")[sinif])


def replik_seviye_olc(x, hedef, tol=None):
    """S4.1 ölçümü: replik yüksekliği (0,4 sn'den kısa ise anlık en yüksek) hedefe ±tol LU içinde mi?"""
    from olcum import ses as O
    tol = so.esik("diyalog_lufs_tolerans") if tol is None else tol
    l = O.lufs(x, SR)
    return l, abs(l - hedef) <= tol


def seviyele(x, hedef):
    """TEK doğrusal kazanç ile hedef yüksekliğe; örnek tepesi −1 dBFS'i aşacaksa kazanç orada durur (sınırlama/sıkıştırma yok)."""
    from olcum import ses as O
    l = O.lufs(x, SR); g = hedef - l; tp = O.ornek_tepe(x)
    if tp + g > -1.0: g = -1.0 - tp
    return (x * O.kazanc(g)).astype("float32"), round(g, 2)


def kelime_tahmini(metin, sure):
    from olcum import ses as O
    k = metin.split(); top = sum(len(w) for w in k) or 1; t = 0.15; out = []
    for w in k:
        d = (sure - 0.3) * len(w) / top; out.append({"w": w, "bas": round(t, 3), "bit": round(t + d * 0.92, 3)}); t += d
    return out


# --- iş ----------------------------------------------------------------------------------------------------------------
def _komsu(rs, i):
    a = rs[i - 1]["metin"] if i > 0 and rs[i - 1].get("sahne_grubu") == rs[i].get("sahne_grubu") else None
    b = rs[i + 1]["metin"] if i + 1 < len(rs) and rs[i + 1].get("sahne_grubu") == rs[i].get("sahne_grubu") else None
    return a, b


def tts_hazirla(film, rs, saglayici=None, kapsam="ANIMATIK", asama="A12"):
    """rs: so.replikler() alt kümesi. (çıkış kodu, rapor yolu, rapor)."""
    from olcum import ses as O
    sahte = so.sahte_mi(film, saglayici)
    olmayan = []; zin = so.zincir("tts", film, saglayici_=saglayici, hazir_olmayan=olmayan)
    if not zin:
        neden = "; ".join("%s: %s" % (x["saglayici"], x["neden"]) for x in olmayan) or "zincir boş"
        log(f"!! hazır TTS sağlayıcısı yok: {neden}")
        return so.ORTAM, None, None
    asr = (so.zincir("asr", film, saglayici_=saglayici) or [None])[0]
    D = diyalog_oku(film); olc, yaz_maddeleri = [], []
    sesler = {}
    for r in rs:
        v = so.karakter_sesi(film, r["karakter"])
        if not v.get("voice_id") and sahte: v = {"voice_id": f"sahte_{r['karakter']}", "kaynak": "sahte"}
        sesler[r["id"]] = v
    s0 = zin[0]
    # BUTK: önbelleksiz toplam harf (kredili sağlayıcı)
    if getattr(s0, "kredili", False):
        yeni = [r for r in rs if sesler[r["id"]].get("voice_id") and not s0.onbellekte_mi(film, r["metin"], sesler[r["id"]]["voice_id"],
                                                                                        sesler[r["id"]].get("seed"))]
        harf = sum(s0.tahmin(r["metin"]) for r in yeni)
        if harf:
            kod = so.kredi_onay(film, f"{asama}-tts-{so.ozet(*[r['id'] + r['metin'] for r in yeni], n=8)}", harf, "film", s0.ad)
            if kod: log(f"!! AI84 bütçesi yetmiyor ({harf} kredi; BUTK)"); return so.BUTCE, None, None
    for i, r in enumerate(rs):
        rid = r["id"]; v = sesler[rid]; kay = D["replikler"].get(rid) or {}
        if not v.get("voice_id"):
            olc.append(so.m("S2.ses", "HATA", birim=rid, plan=None, olcu="karakterin seçilmiş sesi yok", esik="ses_sec --sec (A10c)",
                            oneri="ses seçimi; sessiz geri dönüş yok")); continue
        h = so.ozet(v["voice_id"], getattr(s0, "model", s0.ad), r["metin"], v.get("seed"), n=8)
        rel = os.path.join("SESLER", "tts", f"{rid}_{h}.wav"); hedef_yol = os.path.join(film, rel)
        sinif, hedef = seviye_hedefi(r); onceki, sonraki = _komsu(rs, i)
        sonuc = None
        if os.path.exists(hedef_yol) and (kay.get("tts") or {}).get("dosya") == rel.replace("\\", "/"):
            sonuc = {"onbellek": True, "kredi": 0, "sure_sn": kay["tts"]["sure_sn"], "kelimeler": kay.get("kelimeler")}
        else:
            ham = hedef_yol + ".ham.wav"; isk = f"{rid}_{h}"
            for s in zin:
                try:
                    if getattr(s, "kredili", False):
                        if so.gonderilmis(film, isk) and not s.onbellekte_mi(film, r["metin"], v["voice_id"], v.get("seed")):
                            if kay.get("kayip_yeniden") == isk:
                                olc.append(so.m("S2.tts", "HATA", birim=rid, olcu="gönderim kayıp; ikinci kez gönderilmez", esik="toplama"))
                                break
                            kay["kayip_yeniden"] = isk; log(f"   {rid}: önceki gönderim kayıp (önbellekte yok) → bir kez yeniden")
                        so.gonderim(film, f"tts:{rid}", s.tahmin(r["metin"]), isk, "film", s.ad)
                    sonuc = s.tts(film, r["metin"], v["voice_id"], ham, seed=v.get("seed"), onceki=onceki, sonraki=sonraki,
                                  teslim=sinif, replik=rid)
                    sonuc["saglayici"] = s.ad; break
                except Exception as e:
                    k = so.kisit_kodu(e) if hasattr(e, "kod") else None
                    if hasattr(e, "kod") and k is not None:
                        log(f"!! {s.ad}: geçilemez kısıt ({e.kod}); hat durur"); return k, None, None
                    olc.append(so.m("S2.tts", "HATA", birim=rid, olcu=f"{s.ad}: {str(e)[:100]}", esik="TTS üretildi",
                                    oneri="sessiz geri dönüş yok (Flow sesine düşülmez)"))
            if sonuc is None: continue
            x, _ = O.oku(ham); x = O.mono(x)
            x, g = seviyele(x, hedef); O.yaz(hedef_yol, x)
            kel = sonuc.get("kelimeler")
            if not kel and asr is not None:
                try: kel = asr.asr(film, ham, bilinen_metin=r["metin"]).get("kelimeler")
                except Exception: kel = None
            kz = "saglayici" if sonuc.get("kelimeler") else ("asr" if kel else "tahmini")
            if not kel: kel = kelime_tahmini(r["metin"], len(x) / SR)
            try: os.replace(ham, os.path.join(film, "SESLER", "tts", "_ham_" + os.path.basename(hedef_yol)))
            except OSError: pass
            sonuc.update(sure_sn=round(len(x) / SR, 3), kelimeler=kel, kazanc_db=g, kelime_kaynagi=kz)
        x, _ = O.oku(hedef_yol); x = O.mono(x)
        sure = len(x) / SR; l, ok41 = replik_seviye_olc(x, hedef); tp = O.ornek_tepe(x)
        gerek = sure + so.esik("diyalog_giris_payi_sn") + 0.25 * (len(r["cumleler"]) - 1) + so.esik("diyalog_cikis_payi_sn")
        ok213 = gerek <= r["pencere_sn"] + 1e-6
        olc += [so.m("S2.13", "GEC" if ok213 else "HATA", birim=rid, olcu=round(gerek, 3), esik=f"≤ {r['pencere_sn']} sn (plan + L taşması)",
                     oneri=None if ok213 else "böl, ekran dışına taşı ya da 10 sn klip (yönetmen)"),
                so.m("S2.14", "GEC" if tp < so.esik("ornek_tepe_max_dbfs") else "HATA", birim=rid, olcu=round(tp, 2),
                     esik=f"< {so.esik('ornek_tepe_max_dbfs')} dBFS"),
                so.m("S4.1", "GEC" if ok41 else "HATA", birim=rid, olcu=round(l, 2), esik=f"{hedef} ±{so.esik('diyalog_lufs_tolerans')} LUFS ({sinif})")]
        if sonuc.get("kelime_kaynagi") == "tahmini":
            olc.append(so.m("S2.kelime", "OLCULEMEDI", birim=rid, olcu="kelime zamanı harf oranıyla tahmin", esik="hizalama (stable-ts/ASR)"))
        if not ok213 and r.get("plan"):
            yaz_maddeleri.append({"konum": {"plan": int(r["plan"])}, "kapi": "S2", "madde": "S2.13", "kok_neden": "diyalog_kopuk",
                                  "yazar": "yonetmen", "oneri": f"{rid} TTS {round(sure, 2)} sn; gereken {round(gerek, 2)} > pencere "
                                                                f"{r['pencere_sn']} sn: repliği böl, ekran dışına taşı ya da 10 sn klip"})
        kel = sonuc.get("kelimeler") or kay.get("kelimeler") or []
        kay.update({"karakter": r["karakter"], "kaynak_plan": r["plan"], "yol_plan": r["yol"], "senaryo_metin": r["metin"],
                    "cumleler": r["cumleler"], "tr": r["tr"], "teslim": r["teslim"],
                    "tts": {"dosya": rel.replace("\\", "/"), "sure_sn": round(sure, 3), "kelime_sn": round(len(r["metin"].split()) / max(sure, 1e-3), 2),
                            "kredi": sonuc.get("kredi", 0), "ses": v["voice_id"], "saglayici": sonuc.get("saglayici") or kay.get("tts", {}).get("saglayici"),
                            "onbellek": bool(sonuc.get("onbellek")), "gecirilmedi": sonuc.get("gecirilmedi")},
                    "kelimeler": kel, "kelime_kaynagi": sonuc.get("kelime_kaynagi") or kay.get("kelime_kaynagi"),
                    "seviye": sinif, "hedef_lufs": hedef, "olculen_lufs": round(l, 2), "kazanc_db": sonuc.get("kazanc_db", kay.get("kazanc_db")),
                    "pencere": {"bas": (r.get("replik_zaman") or [None])[0], "sn": r["pencere_sn"]}})
        if kay.get("yol_gercek") in (None, "tts"):
            kay["dosya"] = rel.replace("\\", "/"); kay.setdefault("duyulan_metin", r["metin"])
            if kay.get("yol_gercek") is None: kay["duyulan_metin"] = r["metin"]
        kay.setdefault("merdiven", []); kay.setdefault("denetim", {})
        kay["denetim"]["S2_T1"] = "GEC" if (ok213 and ok41) else "HATA"
        D["replikler"][rid] = kay
        log(f"   {rid} [{r['karakter']}] {round(sure, 2)} sn · {round(l, 1)} LUFS ({sinif}) · {'önbellek' if sonuc.get('onbellek') else sonuc.get('saglayici')}"
            f"{'' if ok213 else ' · SIĞMIYOR'}")
    diyalog_yaz(film, D)
    ys = so.yaz_ekle(film, yaz_maddeleri, asama) if yaz_maddeleri else {"eklenen": [], "reddedilen": []}
    if not olc: olc.append(so.m("S2.replik", "GEC", olcu="replik yok"))
    yol, rap = so.rapor(film, "S2", kapsam, olc, asama=asama, birimler=[r["id"] for r in rs], arac=SURUM,
                        ek={"yeniden_yaz": ys.get("eklenen"), "reddedilen_yaz": len(ys.get("reddedilen") or [])}, gorev_raporu=False)
    return so.BITTI, yol, rap


def parti(film, n, kesit=False, saglayici=None):
    rs = so.replikler(film); S = so.sahneler(film)
    partiler = {p.get("no"): p.get("parti") for p in S.get("sahneler") or []}
    if kesit:
        bp = ortak.json_oku(os.path.join(film, "BLOK_PLANI.json"), {}) or {}
        kes = {pl for b in bp.get("bloklar") or [] if b.get("ad") == "KESIT" or b.get("kesit") for pl in b.get("planlar") or []}
        rs = [r for r in rs if r["plan"] in kes] if kes else rs
    elif n is not None: rs = [r for r in rs if str(partiler.get(r["plan"])) == str(n)]
    tts_r = [r for r in rs if r["yol"] == "tts"]; veo_r = [r for r in rs if r["yol"] != "tts"]
    kod, yol, rap = tts_hazirla(film, tts_r, saglayici, kapsam=f"PARTI{n if not kesit else 'KESIT'}", asama="A14a" if kesit else "A15")
    if kod: return kod
    if veo_r:
        p = os.path.join(HERE, "ses_donustur.py")
        if not os.path.exists(p):
            log(f"!! {len(veo_r)} replik veo_donustur/veo_ham yolunda; ses_donustur.py (video sonrası ses dilimi) bu kurulumda yok."); return so.ORTAM
        arg = [sys.executable, p, "--parti", str(n)] + (["--kesit"] if kesit else []) + ["--film", film]
        if saglayici: arg += ["--saglayici", saglayici]
        return subprocess.run(arg).returncode
    return so.BITTI


def main(argv):
    if argv and not argv[0].startswith("--") and "--film" not in argv:
        import seslendir_v1                                  # v1 SAHNELER (ortak.sahneler_oku v2'de 4 ile çıkar)
        seslendir_v1.Voicer(argv[0]).run(); return 0
    try: film = so.film_coz(so.arg(argv, "--film"))
    except (ValueError, ortak.YolYok) as e: log(f"!! {e}"); return so.ORTAM
    if not os.path.exists(os.path.join(film, "SAHNELER.json")): log("!! SAHNELER.json yok"); return so.HATA
    sg = so.arg(argv, "--saglayici")
    if "--animatik" in argv:
        kod, yol, rap = tts_hazirla(film, so.replikler(film), sg)
        if rap: log(f"S2 ANIMATIK → {rap['sonuc']} ({os.path.relpath(yol, film)})")
        return kod
    if "--parti" in argv:
        n = so.arg(argv, "--parti"); n = None if (n or "").startswith("--") else n
        return parti(film, n, "--kesit" in argv, sg)
    log(__doc__); return so.ORTAM


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
