"""GEMİNİ DENEME — Ö0-e: 1 Gemini paketi (30 plan; plan başına 2 ve 3 aday) + Gemini API (AI Studio) ücretsiz katmanı: görsel kotası ve
fiyatı, video ve ses girişi, katman, veri kullanım koşulu (TASARIM §1.2 Ö0-e, D-16, D-19; emsal: gemini_paket.py, gemini_al.py).

Kullanım (film.py olcum0 calis e … ile ya da doğrudan):
  python gemini_deneme.py durum [--json]
  python gemini_deneme.py paket --b3 <B3 SAHNELER.json> [--b3-kok <B3 klasörü>] [--plan 30]
        B3 planlarından ölçüm paketi: ilk yarısı plan başına 2, ikinci yarısı 3 aday. Paket Masaüstü\\GEMINI GORSEL ISTEM\\O0E_GORSEL_NN\\
        (gemini_paket biçimi); kullanıcı Gemini'ye verir, dönen ZIP'i <veri>\\BILGI\\OLCUM0\\O0e_PAKET\\GELENLER\\'e koyar (fiziksel iş).
  python gemini_deneme.py al [--zip <yol>]          ZIP'i gemini_al ile açar; kol başına teslim oranı (2 ve 3 aday) ve süre
  python gemini_deneme.py api [--video <mp4>] [--ses <wav|mp3>] [--paket-api] [--gorsel-n 2]
        API yoklaması: metin, video girişi, ses girişi, görsel (--paket-api: paketin bütün görselleri API'den; ilk 429'da durur).
        Katman bilinen "ucretli" ise ve izinler.gemini_api_ucretli + usd_tavan_film > 0 yoksa API'ye hiç gidilmez (dolar harcanmaz).
  python gemini_deneme.py rapor [--kapat]           O0e.json kararları + OLCUM0.json; --kapat: eksik parça "ölçülemedi" ile kapanır
Kararlar (O0e.json üst düzey; saglayicilar/gemini_api.o0e ve olcek okur):
  gemini_katman  ucretsiz (429 gövdesinde "free_tier" ya da kurulum kaydı) | ucretli (yalnız kaydı varsa) | bilinmiyor
  video_girisi / ses_girisi  true (200) | false (400: biçim kabul edilmedi) | null (denenemedi, kota, ağ)  → false ise izleyici/dinleyici kapalı
  gorsel_uygun = gemini_api_paket  yalnız paketin bütün görselleri API'den 429'suz geldiyse ve katman ücretli değilse true
  uc_aday_teslim  3 adaylı kolda teslim oranı ≥ 0,9 (tahmin)  (D-16: 3 aday ancak bu + karar 6 testiyle açılır)
  lisans_istegi  veri kullanım koşulu LISANSLAR.json "gemini_api_ucretsiz" satırında doğrulanacak (geliştirme oturumu işi)
Anahtar yalnız istek başlığında gider (gemini_api ile aynı yol); hiçbir yere yazılmaz, yazdırılmaz.
Çıkış kodları: 0 tamam · 1 HATA · 2 KULLANICI (ZIP yok, anahtar yok) · 4 ORTAM (bulut) · 8 BEKLE (kota).
"""
import os, sys, re, json, glob, time, base64, shutil, statistics
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
for _p in (ARACLAR, HERE):
    if _p not in sys.path: sys.path.insert(0, _p)
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import ortak, ortak_o0 as o0

SURUM = "gemini_deneme 1.0"
BITTI, HATA, KULLANICI, ORTAM, BEKLE = 0, 1, 2, 4, 8
PAKET_ONEK = "O0E_GORSEL"
UC_ADAY_ORAN = 0.9                     # tahmin
API_ARA_SN = 6.0                       # ücretsiz katman dakika sınırına saygı (tahmin); testlerde 0
BICIM = "Every image is 16:9 landscape, 1376x768 pixels (never portrait, never square)."


class Dur(Exception):
    def __init__(self, msg, kod=HATA): super().__init__(msg); self.kod = kod


def paket_kok(): return os.path.join(o0.kok(), "O0e_PAKET")
def api_kok(): return os.path.join(o0.kok(), "O0e_API")


def durum_oku():
    d = o0.oku("e")
    return d if d else {"durum": "hazir", "paket": None, "api": None}


def yaz(d):
    d.setdefault("durum", "suruyor")
    return o0.yaz("e", d, arac=SURUM)


# ---------------------------------------------------------------- paket (kullanıcı taşır)
def b3_planlari(b3_sahneler, b3_kok=None, n=30):
    """B3 SAHNELER.json (v1 ya da v2) → [{no, istem, referanslar: [yol]}] (görsel istemi olan ilk n plan)."""
    S = ortak.json_oku(b3_sahneler, None)
    if not isinstance(S, dict): raise Dur(f"B3 SAHNELER.json okunamadı: {b3_sahneler}", KULLANICI)
    kok = b3_kok or os.path.dirname(os.path.abspath(b3_sahneler)); K = S.get("karakterler") or {}; out = []
    for p in S.get("sahneler") or []:
        ist = p.get("gorsel_istem") or ((p.get("uretim") or {}).get("gorsel") or {}).get("istem")
        if not ist or not isinstance(p.get("no"), (int, float)): continue
        refs = []
        for r in (p.get("referans") or [])[:2]:
            y = (K.get(r) or {}).get("ref") if isinstance(r, str) else None
            if y and os.path.isfile(os.path.join(kok, y)): refs.append(os.path.join(kok, y))
        out.append({"no": int(p["no"]), "istem": ist, "referanslar": refs})
        if len(out) >= n: break
    if len(out) < n: raise Dur(f"B3'te görsel istemi olan {len(out)} plan var ({n} gerekiyor).", KULLANICI)
    return out


def paket(planlar):
    """Ölçüm paketini yazar: ilk yarı 2 aday, ikinci yarı 3 aday. (paket sözlüğü)."""
    import gemini_paket as gp
    d = durum_oku()
    if (d.get("paket") or {}).get("ad"): raise Dur(f"Ö0-e paketi zaten var ({d['paket']['ad']}).", BITTI)
    kok = paket_kok(); os.makedirs(os.path.join(kok, "GELENLER", "_PAKETLER"), exist_ok=True)
    n = 1
    while os.path.exists(os.path.join(gp.paket_kok(), f"{PAKET_ONEK}_{n:02d}")): n += 1
    ad = f"{PAKET_ONEK}_{n:02d}"; hedef = os.path.join(gp.paket_kok(), ad); os.makedirs(os.path.join(hedef, "REFERANSLAR"))
    yari = len(planlar) // 2; bek = {}; kol = {"2": [], "3": []}; bloklar = []
    for i, p in enumerate(planlar):
        k = 2 if i < yari else 3; kol[str(k)].append(p["no"]); rr = []
        for r in p["referanslar"]:
            ra = "R_%03d_%s" % (p["no"], re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(r)))
            shutil.copyfile(r, os.path.join(hedef, "REFERANSLAR", ra)); rr.append(ra)
        for h in "abc"[:k]:
            dosya = "%03d_%s.jpg" % (p["no"], h)
            bloklar.append({"dosya": dosya, "referans": rr, "istem": p["istem"] + ("" if h == "a" else f" (take {h}: a different take of the same moment)")})
            bek[dosya] = {"tur": "gorsel", "plan": p["no"], "aday": h, "kol": k}
    with open(os.path.join(hedef, "GOREV.txt"), "w", encoding="utf-8") as f: f.write(gp.GOREV_METNI.format(bicim=BICIM, zip_adi=f"{ad}.zip"))
    with open(os.path.join(hedef, "ISTEMLER.txt"), "w", encoding="utf-8") as f:
        for b in bloklar:
            f.write(f"=== {b['dosya'][:-4]} ===\nFILE NAME: {b['dosya']}\nREFERENCE IMAGES: {', '.join(b['referans']) or 'none'}\nPROMPT: {b['istem']}\n\n")
    man = {"_surum": 1, "paket": ad, "tur": "gorsel", "film_tur": 1, "zip_adi": f"{ad}.zip", "klasor": hedef, "olusturma": o0.zaman(),
           "arac_surum": SURUM, "beklenen": bek, "olcum0": "Ö0-e"}
    ortak.atomik_yaz(os.path.join(hedef, "PAKET.json"), man)
    ortak.atomik_yaz(os.path.join(kok, "GELENLER", "_PAKETLER", f"{ad}.json"), man)
    d["paket"] = {"ad": ad, "klasor": hedef, "olusturma": man["olusturma"], "olusturma_epoch": time.time(), "plan": len(planlar),
                  "kol": kol, "beklenen": len(bek), "bloklar": bloklar, "referanslar": {p["no"]: p["referanslar"] for p in planlar}}
    yaz(d)
    o0.deneme("e", "paket", {"plan": len(planlar), "gorsel": len(bek)}, "kullaniciya_verildi", "30 plan; 2 ve 3 aday kolları")
    return d["paket"]


def al(zip_yol=None):
    import gemini_al
    d = durum_oku(); p = d.get("paket") or {}
    if not p.get("ad"): raise Dur("Önce paket: gemini_deneme.py paket --b3 <B3 SAHNELER.json>.", KULLANICI)
    kok = paket_kok(); zler = [zip_yol] if zip_yol else glob.glob(os.path.join(kok, "GELENLER", "*GORSEL*.zip"))
    zaman = max((os.path.getmtime(z) for z in zler if os.path.exists(z)), default=None)
    kod, rap = gemini_al.al(kok, "gorsel", zip_yol)
    if kod == 2: raise Dur(f"Gemini ZIP'i henüz yok: {p['ad']}.zip dosyasını {os.path.join(kok, 'GELENLER')} klasörüne koy.", KULLANICI)
    alinan = {}
    for a in (rap or {}).get("alinan") or []:
        m = re.match(r"(\d{3})_([a-c])", os.path.basename(a["hedef"]))
        if m: alinan.setdefault(int(m.group(1)), set()).add(m.group(2))
    kol = {}
    for k, nolar in (p.get("kol") or {}).items():
        bek = len(nolar) * int(k); gel = sum(len(alinan.get(int(n), ())) for n in nolar)
        kol[k] = {"plan": len(nolar), "beklenen": bek, "gelen": gel, "oran": round(gel / float(bek), 3) if bek else None,
                  "tam_plan": sum(1 for n in nolar if len(alinan.get(int(n), ())) >= int(k))}
    p["sonuc"] = {"kol": kol, "reddedilen": len((rap or {}).get("reddedilen") or []), "eslesmeyen": len((rap or {}).get("eslesmeyen") or []),
                  "sure_dk": round((zaman - p["olusturma_epoch"]) / 60.0, 1) if zaman and p.get("olusturma_epoch") else None,
                  "zaman": o0.zaman()}
    o3 = (kol.get("3") or {}).get("oran")
    d["uc_aday_teslim"] = bool(o3 is not None and o3 >= UC_ADAY_ORAN)
    yaz(d)
    o0.deneme("e", "paket_teslim", kol, "uc_aday_teslim" if d["uc_aday_teslim"] else "uc_aday_yetersiz",
              f"3 adaylı kolda teslim oranı {o3} (eşik {UC_ADAY_ORAN}, tahmin); 3 aday ancak karar 6 testiyle açılır (D-16)")
    return p["sonuc"]


# ---------------------------------------------------------------- API yoklaması
def _katman_kaydi():
    try: g = ortak.json_oku(os.path.join(ortak.yollar()["ayarlar"], "GEMINI_DURUMU.json"), {}) or {}
    except ortak.YolYok: g = {}
    return None if g.get("sahte") else g.get("gemini_katman")


def _ucretli_izinli():
    try: a = ortak.json_oku(os.path.join(ortak.yollar()["ayarlar"], "FILM_AYAR.json"), {}) or {}
    except ortak.YolYok: a = {}
    return bool((a.get("izinler") or {}).get("gemini_api_ucretli")) and ((a.get("butce") or {}).get("usd_tavan_film") or 0) > 0


class Yoklayici:
    """Tek tek istek; gemini_api'nin taşıyıcı imzası (yontem, url, govde, basliklar) → (durum, gövde, başlıklar). Anahtar yalnız başlıkta."""
    def __init__(self, tasiyici=None, ara_sn=API_ARA_SN):
        from saglayicilar import gemini_api as ga
        self.ga = ga; self.s = ga.GeminiAPI(tasiyici=tasiyici); self.ara = ara_sn; self.free_tier = False; self.son = 0.0

    def istek(self, model, parcalar, json_cevap=True):
        if self.ara and time.time() - self.son < self.ara: time.sleep(self.ara - (time.time() - self.son))
        govde = {"contents": [{"role": "user", "parts": parcalar}]}
        if json_cevap: govde["generationConfig"] = {"responseMimeType": "application/json"}
        st, cevap, _ = self.s.tasiyici("POST", f"{self.ga.URL}/models/{model}:generateContent", json.dumps(govde).encode("utf-8"),
                                       {"Content-Type": "application/json", "x-goog-api-key": self.s._anahtar()})
        self.son = time.time()
        ham = cevap if isinstance(cevap, (bytes, bytearray)) else str(cevap or "").encode()
        if st == 429 and b"free_tier" in ham.lower(): self.free_tier = True
        try: j = json.loads(ham.decode("utf-8") or "{}")
        except ValueError: j = {}
        return st, j, ham[:400].decode("utf-8", "replace")

    def dosya(self, yol): return self.s._dosya_parcasi(yol)


def _giris_karari(st):
    if st == 200: return True
    if st == 400: return False
    return None


def api(tasiyici=None, video=None, ses=None, paket_api=False, gorsel_n=2, ara_sn=API_ARA_SN):
    from saglayicilar import gemini_api as ga
    from saglayicilar import Kisitlandi
    d = durum_oku()
    if not ga.anahtar_var():
        raise Dur("Gemini anahtarı yok: AYARLAR\\gemini_anahtar.txt boş. Google AI Studio'dan (faturalandırma açmadan) ücretsiz anahtar al, "
                  "dosyanın ilk satırına yapıştır, GEMINI_TEST.bat'a çift tıkla.", KULLANICI)
    katman = _katman_kaydi() or "bilinmiyor"
    if katman == "ucretli" and not _ucretli_izinli():
        d["api"] = {"zaman": o0.zaman(), "atlandi": "katman ücretli; izin + dolar tavanı yok → API'ye gidilmedi"}
        d.update(gemini_katman="ucretli", gorsel_uygun=False, gemini_api_paket=False); yaz(d); return d["api"]
    y = Yoklayici(tasiyici, ara_sn); r = {"zaman": o0.zaman()}
    try:
        st, j, ham = y.istek(ga.MODEL_GOZLEM, [{"text": 'Reply only with the JSON {"ok": true}.'}])
        r["metin"] = {"durum": st, "ozet": None if st == 200 else ham[:200]}
        if st in (401, 403): raise Dur("Gemini anahtarı geçersiz ya da yetkisiz (401/403).", KULLANICI)
        vid = video or next(iter(sorted(glob.glob(os.path.join(o0.kok(), "O0b_klipler", "*.mp4")))), None)
        if vid and os.path.isfile(vid):
            st, j, ham = y.istek(ga.MODEL_GOZLEM, [y.dosya(vid), {"text": 'Describe this clip in one sentence as JSON {"tarif": "..."}.'}])
            r["video"] = {"durum": st, "dosya": os.path.basename(vid), "ozet": None if st == 200 else ham[:200]}
        else: r["video"] = {"durum": None, "neden": "deneme klibi yok (--video ya da Ö0-b klibi)"}
        sd = ses or _ses_cikar(vid)
        if sd and os.path.isfile(sd):
            st, j, ham = y.istek(ga.MODEL_GOZLEM, [y.dosya(sd), {"text": 'Is there speech in this audio? Answer as JSON {"konusma": true|false}.'}])
            r["ses"] = {"durum": st, "dosya": os.path.basename(sd), "ozet": None if st == 200 else ham[:200]}
        else: r["ses"] = {"durum": None, "neden": "deneme sesi yok (--ses ya da ffmpeg ile klipten)"}
        r["gorsel"] = _gorsel_yokla(y, ga, d.get("paket") or {}, paket_api, gorsel_n)
    except Kisitlandi as e:
        r["hata"] = {"kod": e.kod, "mesaj": str(e)[:160]}
    if y.free_tier: katman = "ucretsiz"
    g = r.get("gorsel") or {}
    d["api"] = r
    d["gemini_katman"] = katman
    d["video_girisi"] = _giris_karari((r.get("video") or {}).get("durum"))
    d["ses_girisi"] = _giris_karari((r.get("ses") or {}).get("durum"))
    d["gorsel_kota_gozlenen"] = g.get("basarili")
    d["gorsel_uygun"] = bool(katman != "ucretli" and g.get("paket_api") and g.get("tamam"))
    d["gemini_api_paket"] = d["gorsel_uygun"]
    d["fiyat"] = {"gorsel_usd": 0 if katman == "ucretsiz" else None, "olculemedi": katman != "ucretsiz",
                  "not": "ücretli fiyat AI Studio fiyat sayfasından okunur (bellekten değil)"}
    yaz(d)
    for ad, v in (("video_girisi", d["video_girisi"]), ("ses_girisi", d["ses_girisi"])):
        o0.deneme("e", ad, (r.get(ad.split("_")[0]) or {}).get("durum"), {True: "kabul", False: "red", None: "olculemedi"}[v],
                  "izleyici/dinleyici açılma kuralı (D-19)")
    o0.deneme("e", "gorsel_api", g, "uygun" if d["gorsel_uygun"] else "uygun_degil",
              "paketin bütün görselleri ücretsiz katmanda 429'suz geldiyse API'ye geçilir; değilse paket yolu")
    return r


def _ses_cikar(vid):
    if not vid or not os.path.isfile(vid) or not shutil.which("ffmpeg"): return None
    os.makedirs(api_kok(), exist_ok=True); h = os.path.join(api_kok(), "ses_deneme.mp3")
    import subprocess
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", vid, "-vn", "-ac", "1", "-b:a", "96k", h])
    return h if r.returncode == 0 and os.path.isfile(h) else None


def _gorsel_yokla(y, ga, p, paket_api, n):
    bl = list(p.get("bloklar") or [])
    if not bl: return {"denendi": 0, "neden": "paket yok"}
    hedef = bl if paket_api else bl[:max(0, int(n))]
    os.makedirs(api_kok(), exist_ok=True); ok = 0; ilk429 = None; hata = []
    refler = p.get("referanslar") or {}
    for i, b in enumerate(hedef):
        no = int(b["dosya"][:3]); parca = [y.dosya(r) for r in (refler.get(no) or refler.get(str(no)) or []) if os.path.isfile(r)]
        st, j, ham = y.istek(ga.MODEL_GORSEL, parca + [{"text": b["istem"]}], json_cevap=False)
        if st == 429: ilk429 = i; break
        if st != 200: hata.append({"dosya": b["dosya"], "durum": st}); continue
        veri = None
        for c in ((j.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []:
            dd = c.get("inline_data") or c.get("inlineData")
            if dd and dd.get("data"): veri = base64.b64decode(dd["data"]); break
        if veri is None: hata.append({"dosya": b["dosya"], "durum": "gorsel_yok"}); continue
        with open(os.path.join(api_kok(), b["dosya"]), "wb") as f: f.write(veri)
        ok += 1
    return {"paket_api": bool(paket_api), "denendi": len(hedef) if ilk429 is None else ilk429 + 1, "basarili": ok, "ilk_429": ilk429,
            "hata": hata, "tamam": ilk429 is None and not hata and ok == len(hedef) and len(hedef) == len(bl)}


# ---------------------------------------------------------------- rapor
LISANS_ISTEGI = {"anahtar": "gemini_api_ucretsiz", "kaynak": "https://ai.google.dev/gemini-api/terms",
                 "istek": "Ücretsiz katmanın veri kullanım koşulunu kaynağından oku; veri/LISANSLAR.json 'gemini_api_ucretsiz' satırında "
                          "dogrulama + dogrulama_tarihi alanlarını güncelle (geliştirme oturumu, PR ile).",
                 "kullaniciya_bilgi": "Ücretsiz Gemini katmanında Google gönderilen dosyaları ürünlerini geliştirmek için kullanabilir "
                                      "(bellekten; doğrulanacak). Bu yüzden yalnız filmin kendi dosyaları gönderilir."}


def rapor(kapat=False):
    d = durum_oku()
    d["lisans_istegi"] = LISANS_ISTEGI
    paket_bitti = bool((d.get("paket") or {}).get("sonuc")); api_bitti = bool(d.get("api"))
    if api_bitti and (paket_bitti or kapat):
        if not paket_bitti: d.setdefault("uc_aday_teslim", None); d["paket_olculemedi"] = True
        d["durum"] = "bitti"
    elif kapat:
        d.update(gemini_katman=d.get("gemini_katman") or "bilinmiyor", video_girisi=d.get("video_girisi"),
                 ses_girisi=d.get("ses_girisi"), gorsel_uygun=bool(d.get("gorsel_uygun")), gemini_api_paket=bool(d.get("gemini_api_paket")),
                 durum="bitti", api_olculemedi=not api_bitti, paket_olculemedi=not paket_bitti)
    yaz(d)
    if d["durum"] == "bitti":
        o0.deneme("e", "katman", d.get("gemini_katman"), d.get("gemini_katman"), "429 'free_tier' gövdesi ya da kurulum kaydı")
        o0.deneme("e", "lisans", LISANS_ISTEGI["anahtar"], "dogrulanacak", LISANS_ISTEGI["istek"])
    return {k: d.get(k) for k in o0.OZET_ANAHTAR["e"] + ("lisans_istegi",)}


def durum_metni():
    d = durum_oku(); p = d.get("paket") or {}
    sonraki = "paket" if not p.get("ad") else ("al" if not p.get("sonuc") else None)
    if not d.get("api"): sonraki = sonraki or "api"
    if sonraki is None and d.get("durum") != "bitti": sonraki = "rapor"
    return {"durum": o0.durum("e"), "paket": p.get("ad"), "paket_alindi": bool(p.get("sonuc")), "api": bool(d.get("api")), "sonraki": sonraki}


def _arg(argv, ad, v=None): return argv[argv.index(ad) + 1] if ad in argv and argv.index(ad) + 1 < len(argv) else v


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    k = argv[0]
    try:
        if k == "durum": print(json.dumps(durum_metni(), ensure_ascii=False)); return 0
        if o0.ortam() == "bulut": print("Ö0-e yalnız kullanıcının bilgisayarında yapılır."); return ORTAM
        if k == "paket":
            b3 = _arg(argv, "--b3")
            if not b3: print("--b3 <B3 SAHNELER.json> gerekli."); return KULLANICI
            p = paket(b3_planlari(b3, _arg(argv, "--b3-kok"), int(_arg(argv, "--plan", "30"))))
            print(f"Gemini paketi hazır: {p['klasor']}\nBu klasördeki GOREV.txt ve ISTEMLER.txt'i (ve REFERANSLAR'ı) Gemini'ye ver. "
                  f"Dönen {p['ad']}.zip dosyasını şu klasöre koy: {os.path.join(paket_kok(), 'GELENLER')}"); return 0
        if k == "al": print(json.dumps(al(_arg(argv, "--zip")), ensure_ascii=False)); return 0
        if k == "api":
            r = api(video=_arg(argv, "--video"), ses=_arg(argv, "--ses"), paket_api="--paket-api" in argv,
                    gorsel_n=int(_arg(argv, "--gorsel-n", "2")))
            print(json.dumps({x: r.get(x) for x in ("metin", "video", "ses", "gorsel", "hata", "atlandi")}, ensure_ascii=False))
            return BEKLE if (r.get("hata") or {}).get("kod") == "kota" else 0
        if k == "rapor": print(json.dumps(rapor("--kapat" in argv), ensure_ascii=False)); return 0
    except Dur as e: print(str(e)); return e.kod
    except ortak.YolYok as e: print(str(e)); return ORTAM
    print(__doc__); return ORTAM


if __name__ == "__main__":
    sys.exit(main())
