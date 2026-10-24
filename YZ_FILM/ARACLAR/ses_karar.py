"""SES KARAR — ses merdiveni ve S2 replik kapısı (TASARIM §2.2 "Ses merdiveni", §6.6; [SM2] §4.7.3, §4.5.11).

Kullanım:
  python ses_karar.py --film <film> [--saglayici sahte] [--tur 1]   → _RAPOR/S2_FILM_t<tur>.json (+ kuyruk, istek dosyaları)
Girdi: SESLER/diyalog.json v2 (metin_kapisi: SC1 / ses_donustur --hizala; donusum: ses_donustur), _HIKAYE_ODASI/REPLIK_KABUL.json
(hikaye-yazari·replik_kabul kararları), SAHNELER.json (ağız görünürlüğü), KURGU_PLANI (kurguda ağız görünüyor mu).
Hata türüne göre merdiven (her basamak ölçülür; 0 kredili ve kaliteyi düşürmeyen basamak önce; kredili basamak 0 kredi kuralından
geçer: sifir_kredi.denendi + gerekçe "kalite (KK6)"; yeniden çekim plan başına ≤ 2, soy sayacı kuyruk.py'de):
  Veo konuşmadı / yanlış kişi / dinleyen konuştu (S2.1, S2.5): yeniden çekim CORRECTION (≤ 2) → tts_dudak → ekran dışına taşı (tts)
      → yönetmen onarımı → açık rapor
  Gri bant WER 0,10–0,25 ya da `tasidigi` kelimesi değişti (S2.2, S2.4): replik_kabul (yeni örnek, 0 kredi; kabul → duyulan_metin altyazıya)
      → ret: "word for word" yeniden çekim (≤ 2) → tts_dudak → yönetmen onarımı → açık rapor. WER > 0,25 doğrudan yeniden çekimle başlar.
  Ad yanlış (S2.3): ad CORRECTION ile yeniden çekim (≤ 2; ikincide istem_kalibi ders adayı) → tts_dudak → ekran dışına taşı → açık rapor
  Dönüşüm kalitesi (S2.8 gecikme > 20 ms H, S2.9 benzerlik < 0,70 H, S2.10 WER artışı > 0,05 B): sonraki motor (hemen denenir, yeniden
      ölçülür) → kurguda ağız görünmüyorsa tts → ai84_vc (yalnız BUTK isteği; film tavanı 20 bin) → tts_dudak → teslim değişikliği isteği
  S2.6 hız 1,8–3,2 kelime/sn (B) · S2.7 |F0 kaydırma| ≤ 6 yt (B) · S2.12 TTS esnetme ≤ %8 (H) · S2.14 örnek tepe < −0,1 dBFS (H; tek kazançla
  düzeltilir) · S2.16 aksan (dinleyici yoksa ÖLÇÜLEMEDİ).
Seviye: bekleyen kredili/yeniden işleme basamağı HATA (aşama geçmez, kuyruk açılır) · replik_kabul bekleniyor BAYRAK · kabul GEÇ ·
merdiven tükendi → açık rapor (BAYRAK; FILM_SONU_RAPORU'na). Denenen her basamak replikler.<id>.merdiven[]'e yazılır.
İstek dosyaları: SESLER/DUDAK_ISTEK.json (dudak_denetim --musetalk), SESLER/TTS_ISTEK.json (seslendir), SESLER/AI84_VC_ISTEK.json (BUTK),
KURGU/SES_ISTEKLERI.json (kurgucu: ekran_disi), _HIKAYE_ODASI/YONETMEN_ONARIM_ISTEK.json.
Çıkış kodları: 0 S2 GEÇ/BAYRAK · 1 S2 HATA · 2 diyalog.json yok · 4 kullanım.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kurgu_ortak as ko, ses_donustur_ana as sda

SURUM = "ses_karar 1.0"
YENIDEN_CEKIM_MAX = 2
GRI, WER_H = (0.10, 0.25), 0.25
HIZ = (1.8, 3.2)
F0_MAX, GECIKME_MAX_MS, BENZERLIK_MIN, WER_ARTIS_MAX, ESNETME_MAX, TEPE_MAX = 6, 20, 0.70, 0.05, 0.08, -0.1
MERDIVEN = {
    "konusmadi": ["yeniden_cek", "tts_dudak", "ekran_disi_tts", "yonetmen_onarim", "acik_rapor"],
    "gri": ["replik_kabul", "yeniden_cek", "tts_dudak", "yonetmen_onarim", "acik_rapor"],
    "metin": ["yeniden_cek", "tts_dudak", "yonetmen_onarim", "acik_rapor"],
    "ad": ["yeniden_cek", "tts_dudak", "ekran_disi_tts", "acik_rapor"],
    "donusum": ["sonraki_motor", "tts_agiz_gorunmuyor", "ai84_vc", "tts_dudak", "teslim_degisikligi"],
}
SABLON = {"veo_konusmadi": 'CORRECTION: {Ad} speaks the line aloud, lips moving clearly: "{metin}"',
          "veo_metin_sapti": 'CORRECTION: {Ad} says the line exactly, word for word: "{metin}"',
          "ad_yanlis_okundu": 'CORRECTION: say the name exactly as "{okunus}".',
          "yanlis_kisi_konustu": "CORRECTION: only {Ad} speaks; {Diger} listens silently, mouth closed.",
          "dinleyen_konustu": "CORRECTION: only {Ad} speaks; {Diger} listens silently, mouth closed.",
          "aksan_kaydi": "CORRECTION: {Ad} speaks {tarif}."}


def _ad(k): return (k or "").replace("_", " ").title()


def duzeltme(kok_neden, r, pl):
    p = pl.get(r.get("kaynak_plan"), {}); dig = [k.get("id") for k in ko.zanaat(p).get("kadrajdakiler") or [] if k.get("id") != r.get("karakter")]
    mk = r.get("metin_kapisi") or {}
    return SABLON.get(kok_neden, SABLON["veo_konusmadi"]).format(
        Ad=_ad(r.get("karakter")), metin=r.get("veo_metin_istem") or r.get("senaryo_metin") or "", Diger=_ad(dig[0]) if dig else "the other person",
        okunus=mk.get("okunus_yazimi") or mk.get("ad_yazilan") or "", tarif=((p.get("zanaat") or {}).get("ses") or {}).get("veo_ses_tarifi", ""))


def _gecmis(r, tur): return [m for m in r.get("merdiven") or [] if m.get("hata") == tur]


def _cekim_sayisi(r): return sum(1 for m in r.get("merdiven") or [] if m.get("basamak") == "yeniden_cek")


def _sonraki_basamak(r, tur):
    denenen = {m["basamak"] for m in _gecmis(r, tur)}
    for b in MERDIVEN[tur]:
        if b == "yeniden_cek" and _cekim_sayisi(r) >= YENIDEN_CEKIM_MAX: continue
        if b != "yeniden_cek" and b in denenen: continue
        return b
    return None


def _bekliyor(r, tur):
    g = _gecmis(r, tur); return bool(g) and g[-1].get("sonuc") in ("kuyrukta", "istendi")


def _agiz_gorunur_kurguda(kok, r, pl):
    _, kp = ko.kurgu_plani(kok)
    for d in (kp or {}).get("diyalog") or []:
        if d.get("replik") == r.get("_id"): return bool(d.get("gorunen_konusan"))
    return (pl.get(r.get("kaynak_plan"), {}).get("_derlenir") or {}).get("agiz_gorunur") in ("tam", "kismi")


def _istek(kok, rel, madde, anahtar="replikler"):
    p = os.path.join(kok, rel); v = ortak.json_oku(p, {}) or {}; v.setdefault(anahtar, [])
    if not any(x.get("replik") == madde.get("replik") and not x.get("yapildi") for x in v[anahtar]): v[anahtar].append(madde)
    ortak.atomik_yaz(p, v)


def basamak_uygula(kok, argv, rid, r, tur, kok_neden, basamak, pl, kuyruk, tarih):
    """Basamağı uygular; (seviye, karar metni) döndürür."""
    kayit = {"hata": tur, "basamak": basamak, "kok_neden": kok_neden, "tarih": tarih}
    plan = r.get("kaynak_plan")
    if basamak == "replik_kabul":
        kayit["sonuc"] = "istendi"; r.setdefault("merdiven", []).append(kayit)
        return "BAYRAK", "hikaye-yazari·replik_kabul bekleniyor (0 kredi; otomatik kabul yok)"
    if basamak == "yeniden_cek":
        kuyruk.append({"plan": plan, "tur": "video", "kok_neden": kok_neden, "seviye": "KRITIK", "cozum": "yeniden_cek",
                       "duzeltme": duzeltme(kok_neden, r, pl), "replik": rid, "dilim": "ses",
                       "sifir_kredi": {"denendi": True, "basamaklar": [3, 4],
                                       "gerekce": "kalite (KK6): ağzı görünen replik; ekran dışına taşıma ya da TTS kaliteyi düşürür"},
                       "kredi_tahmini": ko.esik("kredi_klip_720p", 12)})
        kayit["sonuc"] = "kuyrukta"; kayit["klip_ozet"] = ko.sha1(ko.klip_yolu(kok, plan)); r.setdefault("merdiven", []).append(kayit)
        if kok_neden == "ad_yanlis_okundu" and _cekim_sayisi(r) >= 2:
            try:
                import ders_defteri as dd
                dd.kaydet("kapi_hatasi", kaynak="kapi", belirti=f"{rid}: ad ikinci kez yanlış okundu", film=os.path.basename(kok),
                          asama="A15", kapi="S2", madde="S2.3", plan=plan, kategori="istem_kalibi",
                          eylem="ders_adayi:istem_kalibi (veo_metin okunuş yazımı)", kanit=[f"SESLER/diyalog.json#{rid}"])
            except Exception as e: kayit["ders"] = f"yazılamadı: {e.__class__.__name__}"
            kayit["ders_adayi"] = "istem_kalibi"
        return "HATA", f"yeniden çekim kuyrukta ({_cekim_sayisi(r)}/{YENIDEN_CEKIM_MAX}; CORRECTION şablonu)"
    if basamak == "tts_dudak":
        _istek(kok, os.path.join("SESLER", "DUDAK_ISTEK.json"), {"replik": rid, "plan": plan, "neden": kok_neden})
        if not ((r.get("tts") or {}).get("dosya")): _istek(kok, os.path.join("SESLER", "TTS_ISTEK.json"), {"replik": rid, "neden": "tts_dudak"})
        kayit["sonuc"] = "istendi"; r.setdefault("merdiven", []).append(kayit)
        return "HATA", "tts_dudak (MuseTalk) istendi; çıktı V2 + S3'ten geçmeli"
    if basamak in ("ekran_disi_tts", "tts_agiz_gorunmuyor"):
        if basamak == "tts_agiz_gorunmuyor" and _agiz_gorunur_kurguda(kok, dict(r, _id=rid), pl):
            kayit["sonuc"] = "uygulanamaz"; r.setdefault("merdiven", []).append(kayit); return None, None
        if basamak == "ekran_disi_tts":
            _istek(kok, os.path.join("KURGU", "SES_ISTEKLERI.json"), {"replik": rid, "op": "ekran_disi", "plan": plan, "kok_neden": kok_neden},
                   "islemler")
        if (r.get("tts") or {}).get("dosya"):
            r["yol_gercek"] = "tts"; r["dosya"] = r["tts"]["dosya"]; kayit["sonuc"] = "uygulandi"
            r.setdefault("merdiven", []).append(kayit); return "GEC", "tts yoluna geçildi (ağız görünmüyor)"
        _istek(kok, os.path.join("SESLER", "TTS_ISTEK.json"), {"replik": rid, "neden": basamak})
        kayit["sonuc"] = "istendi"; r.setdefault("merdiven", []).append(kayit)
        return "HATA", "TTS sesi istendi (seslendir); sonra tts yolu"
    if basamak == "sonraki_motor":
        once = dict(r.get("donusum") or {})
        s = sda.donustur_replik(kok, argv, rid, r, sonraki=True)
        kayit.update(sonuc="denendi" if s == "tamam" else s, olcu={"once": {k: once.get(k) for k in ("motor", "benzerlik", "zarf_gecikme_ms")},
                                                                   "sonra": {k: (r.get("donusum") or {}).get(k) for k in ("motor", "benzerlik", "zarf_gecikme_ms")}})
        r.setdefault("merdiven", []).append(kayit)
        return ("YENIDEN", "sonraki motor denendi") if s == "tamam" else (None, None)
    if basamak == "ai84_vc":
        _istek(kok, os.path.join("SESLER", "AI84_VC_ISTEK.json"), {"replik": rid, "plan": plan, "tavan_film": ko.esik("ai84_vc_tavan_film", 20000),
                                                                   "not": "önce estimate; BUTK bütçe noktası (kredi.py)"})
        kayit["sonuc"] = "istendi"; r.setdefault("merdiven", []).append(kayit)
        return "HATA", "ai84_vc istendi (BUTK; film tavanı 20 bin)"
    if basamak in ("yonetmen_onarim", "teslim_degisikligi"):
        _istek(kok, os.path.join("_HIKAYE_ODASI", "YONETMEN_ONARIM_ISTEK.json"),
               {"replik": rid, "plan": plan, "kok_neden": kok_neden, "istek": basamak,
                "sahip": "yonetmen" if basamak == "yonetmen_onarim" else "hikaye-yazari"})
        kayit["sonuc"] = "istendi"; r.setdefault("merdiven", []).append(kayit)
        return "HATA", f"{basamak} istendi"
    kayit["sonuc"] = "acik_rapor"; r.setdefault("merdiven", []).append(kayit)
    return "BAYRAK", "merdiven tükendi: açık rapor (FILM_SONU_RAPORU)"


def merdiven_yuru(kok, argv, rid, r, tur, kok_neden, pl, kuyruk, tarih, madde, olc):
    for _ in range(len(MERDIVEN[tur]) + 2):
        if _bekliyor(r, tur):
            son = _gecmis(r, tur)[-1]
            olc.append(ko.m(madde, "BAYRAK" if son["basamak"] == "replik_kabul" else "HATA", r.get("kaynak_plan"), replik=rid,
                            kok_neden=kok_neden, karar=f"{son['basamak']} bekleniyor")); return
        b = _sonraki_basamak(r, tur)
        if b is None:
            olc.append(ko.m(madde, "BAYRAK", r.get("kaynak_plan"), replik=rid, kok_neden=kok_neden, karar="merdiven tükendi: açık rapor"))
            return
        sv, karar = basamak_uygula(kok, argv, rid, r, tur, kok_neden, b, pl, kuyruk, tarih)
        if sv is None: continue
        if sv == "YENIDEN": return "yeniden"
        olc.append(ko.m(madde, sv, r.get("kaynak_plan"), replik=rid, kok_neden=kok_neden, karar=karar, basamak=b)); return


def donusum_hatasi(r):
    dn = r.get("donusum") or {}; h = []
    if dn.get("zarf_gecikme_ms") is not None and abs(float(dn["zarf_gecikme_ms"])) > GECIKME_MAX_MS: h.append(("S2.8", "HATA"))
    if dn.get("benzerlik") is not None and float(dn["benzerlik"]) < BENZERLIK_MIN: h.append(("S2.9", "HATA"))
    if dn.get("wer_artis") is not None and float(dn["wer_artis"]) > WER_ARTIS_MAX: h.append(("S2.10", "BAYRAK"))
    return h


def bekleyenleri_kapat(kok, r):
    """Yapılmış basamakları kapatır: yeniden çekimde klip özeti değişti · tts_dudak üretildi · istenen TTS geldi."""
    for m in r.get("merdiven") or []:
        if m.get("sonuc") not in ("kuyrukta", "istendi"): continue
        b = m.get("basamak")
        if b == "yeniden_cek" and m.get("klip_ozet") and ko.sha1(ko.klip_yolu(kok, r.get("kaynak_plan"))) != m["klip_ozet"]: m["sonuc"] = "yapildi"
        elif b == "tts_dudak" and r.get("yol_gercek") == "tts_dudak": m["sonuc"] = "yapildi"
        elif b in ("ekran_disi_tts", "tts_agiz_gorunmuyor") and (r.get("tts") or {}).get("dosya"): m["sonuc"] = "yapildi"


def replik_denetle(kok, argv, rid, r, pl, kabul, kuyruk, tarih, olc):
    bekleyenleri_kapat(kok, r)
    yol = r.get("yol_gercek") or r.get("yol_plan"); plan = r.get("kaynak_plan"); mk = r.get("metin_kapisi")
    if yol in ("veo_donustur", "veo_ham") and r.get("yol_gercek") not in ("tts", "tts_dudak"):
        if not mk:
            olc.append(ko.m("S2_metin_kapisi", "OLCULEMEDI", plan, replik=rid, neden="SC1 hizalaması yok (ses_donustur --hizala)")); return
        konusan = mk.get("konusan_yuz")
        if mk.get("konusma_bulundu") is False or (not r.get("kelimeler") and mk.get("wer", 0) >= 0.99):
            merdiven_yuru(kok, argv, rid, r, "konusmadi", "veo_konusmadi", pl, kuyruk, tarih, "S2.1_konusma", olc); return
        if mk.get("dinleyen_konustu"):
            merdiven_yuru(kok, argv, rid, r, "konusmadi", "dinleyen_konustu", pl, kuyruk, tarih, "S2.5_konusan", olc); return
        if konusan and konusan != r.get("karakter"):
            merdiven_yuru(kok, argv, rid, r, "konusmadi", "yanlis_kisi_konustu", pl, kuyruk, tarih, "S2.5_konusan", olc); return
        if mk.get("ad_dogru") is False:
            merdiven_yuru(kok, argv, rid, r, "ad", "ad_yanlis_okundu", pl, kuyruk, tarih, "S2.3_ad", olc); return
        w = mk.get("wer"); k = (kabul.get(rid) or {}).get("karar")
        if w is not None and float(w) > WER_H and k != "kabul":
            merdiven_yuru(kok, argv, rid, r, "metin", "veo_metin_sapti", pl, kuyruk, tarih, "S2.2_wer", olc); return
        if sda.gri_mi(r):
            if k == "kabul":
                if mk.get("duyulan"): r["duyulan_metin"] = mk["duyulan"]
                if not any(m.get("basamak") == "replik_kabul" and m.get("sonuc") == "kabul" for m in r.get("merdiven") or []):
                    r.setdefault("merdiven", []).append({"hata": "gri", "basamak": "replik_kabul", "sonuc": "kabul", "tarih": tarih})
                olc.append(ko.m("S2.2_S2.4_gri_bant", "GEC", plan, replik=rid, karar="replik_kabul: kabul; altyazı duyulan_metin'den"))
            elif k == "ret":
                for m in _gecmis(r, "gri"):
                    if m["basamak"] == "replik_kabul": m["sonuc"] = "ret"
                merdiven_yuru(kok, argv, rid, r, "gri", "veo_metin_sapti", pl, kuyruk, tarih, "S2.2_S2.4_gri_bant", olc)
            else:
                merdiven_yuru(kok, argv, rid, r, "gri", "veo_metin_sapti", pl, kuyruk, tarih, "S2.2_S2.4_gri_bant", olc)
            if k != "kabul": return
        else:
            olc.append(ko.m("S2.2_wer", "GEC", plan, replik=rid, olcu=w, esik=GRI[0]))
        hz = mk.get("hiz_kelime_sn")
        if hz is not None and not (HIZ[0] <= float(hz) <= HIZ[1]):
            olc.append(ko.m("S2.6_hiz", "BAYRAK", plan, replik=rid, olcu=hz, esik=list(HIZ)))
        aks = mk.get("aksan")
        if aks in (None, "olculemedi"): olc.append(ko.m("S2.16_aksan", "OLCULEMEDI", plan, replik=rid, neden="dinleyici yok"))
        elif aks is False: olc.append(ko.m("S2.16_aksan", "BAYRAK", plan, replik=rid, kok_neden="aksan_kaydi"))
        if yol == "veo_donustur":
            dn = r.get("donusum")
            if not dn: olc.append(ko.m("S2.8_S2.9_donusum", "OLCULEMEDI", plan, replik=rid, neden="dönüşüm yapılmadı")); return
            if dn.get("f0_kaydirma_yt") is not None and abs(int(dn["f0_kaydirma_yt"])) > F0_MAX:
                olc.append(ko.m("S2.7_f0", "BAYRAK", plan, replik=rid, olcu=dn["f0_kaydirma_yt"], esik=F0_MAX))
            if dn.get("benzerlik") is None: olc.append(ko.m("S2.9_benzerlik", "OLCULEMEDI", plan, replik=rid))
            for _ in range(4):
                h = donusum_hatasi(r)
                if not h: olc.append(ko.m("S2.8_S2.9_donusum", "GEC", plan, replik=rid, olcu={k: dn.get(k) for k in ("motor", "benzerlik", "zarf_gecikme_ms")})); break
                madde = "_".join(x[0] for x in h)
                if all(s == "BAYRAK" for _, s in h):
                    olc.append(ko.m(madde, "BAYRAK", plan, replik=rid, olcu=r.get("donusum"), kok_neden="donusum_metalik")); break
                if merdiven_yuru(kok, argv, rid, r, "donusum", "donusum_metalik", pl, kuyruk, tarih, madde, olc) != "yeniden": break
                dn = r.get("donusum") or {}
    if yol == "tts" or r.get("yol_gercek") == "tts":
        es = (r.get("tts") or {}).get("esnetme_oran")
        if es is not None and abs(float(es)) > ESNETME_MAX:
            _istek(kok, os.path.join("SESLER", "TTS_ISTEK.json"), {"replik": rid, "neden": "esnetme > %8: yeniden okut"})
            olc.append(ko.m("S2.12_tts_esnetme", "HATA", plan, replik=rid, olcu=es, esik=ESNETME_MAX, karar="yeniden okutma istendi"))
    p = ko.replik_dosyasi(kok, r, tercih=("dosya",))
    if p:
        a, sr = ko.wav_oku(p); t = ko.tepe_dbfs(a)
        if t >= TEPE_MAX:
            ko.wav_yaz(p, a * ko.kazanc(-1.0 - t), sr)            # tek doğrusal kazanç, −1 dBFS tepe; yeniden ölçülür
            t2 = ko.tepe_dbfs(ko.wav_oku(p)[0])
            olc.append(ko.m("S2.14_tepe", "GEC" if t2 < TEPE_MAX else "HATA", plan, replik=rid, olcu=round(t2, 2), esik=TEPE_MAX,
                            karar=f"tek kazançla düzeltildi ({round(t, 2)} → {round(t2, 2)} dBFS)"))


def karar(kok, argv=()):
    argv = list(argv); dj = ko.diyalog_oku(kok)
    pl = ko.sahne_planlari(kok); kabul = sda._kabul_edilmis(kok); kuyruk, olc = [], []
    tarih = ko.po.zarf("A15", SURUM)["zaman"]
    for rid, r in sorted(dj["replikler"].items()):
        n0 = len(olc)
        replik_denetle(kok, argv, rid, r, pl, kabul, kuyruk, tarih, olc)
        hs = [o["seviye"] for o in olc[n0:]]
        r.setdefault("denetim", {})["S2"] = "HATA" if "HATA" in hs else ("BAYRAK" if any(s in ("BAYRAK", "OLCULEMEDI") for s in hs) else "GEC")
    ko.diyalog_yaz(kok, dj)
    tur = ko.po.tur_no(argv)
    yol, r = ko.po.rapor_yaz(kok, "S2", "FILM", olc, asama="A15", arac=SURUM, tur=tur,
                             birimler=sorted({x.get("kaynak_plan") for x in dj["replikler"].values() if x.get("kaynak_plan") is not None}),
                             varsayilan=os.path.join("_RAPOR", f"S2_FILM_t{tur}.json"), kuyruk=kuyruk,
                             ek={"merdiven": {rid: x.get("merdiven") for rid, x in dj["replikler"].items() if x.get("merdiven")}})
    ko.po.yaz_ozet(r, os.path.basename(yol))
    if kuyruk:
        import kuyruk as q
        s = q.topla(kok, asama="A15")
        print(f"   kuyruk: eklenen {len(s['eklenen'])} · birleşen {len(s['birlesen'])} · reddedilen {len(s['reddedilen'])}", flush=True)
    return yol, r


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    if not os.path.exists(os.path.join(kok, "SESLER", "diyalog.json")): print("!! SESLER/diyalog.json yok", flush=True); return 2
    _, r = karar(kok, argv)
    return ko.po.cikis(r)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
