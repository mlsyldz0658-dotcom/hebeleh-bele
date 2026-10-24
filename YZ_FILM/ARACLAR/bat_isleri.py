"""BAT İŞLERİ — .bat dosyalarının Python yarısı: Türkçe mesajları ve tek işleri bu araç yapar (TASARIM §6.9, §8.2, §8.4).

Kullanım (her .bat tek bir alt komut çağırır; bat_yenile.py üretir):
  python bat_isleri.py film-seti                 FILM_SETI.bat: Claude Code var mı; yoksa ne yapılacağını söyler (4)
  python bat_isleri.py guncelle [--depo <k>]     GUNCELLE.bat: git pull --ff-only (önce fetch + denetim; aşağıda)
  python bat_isleri.py flow-giris [--kuru]       FLOW_GIRIS.bat: Memmet Chrome'unu açar, Flow'a SEN Google ile girersin
  python bat_isleri.py izinler [--goster | --ac <izin> | --kapat <izin> | --usd <sayı> | --mod tam_otomatik|onayli]
                                                 IZINLER.bat: izin paneli (yalnız kullanıcının kendi isteğiyle; argümansız → menü)
  python bat_isleri.py gemini-test [--saglayici sahte]
                                                 GEMINI_TEST.bat: anahtar dosyasının yalnız varlığı/tarihi/boş olmadığı (içerik okunmaz)
  python bat_isleri.py durdur <film>             DURDUR.bat: <film>/DUR yazar; film.py yeni iş başlatmaz (8 BEKLE)
  python bat_isleri.py devam <film>              DEVAM.bat: DUR'u <film>/_ESKI/'ye taşır (silmez); .bat sonra claude --continue
  python bat_isleri.py film-deneme <film>        FILM_DENEME_SAHTE.bat: film.py <film> --saglayici sahte (kredisiz deneme)

GUNCELLE kuralları ([SON] O-5, D-12): .git yoksa (ZIP kurulumu) kapalıdır, bilgi verir (4). İzlenen dosyada yerel değişiklik, yerel commit
(ileri dal) ya da gelen değişikliğin üzerine yazacağı izlenmeyen/yok sayılan bir dosya varsa HİÇBİR ŞEYİ taşımadan durur, tek cümle söyler (2).
Denetim fetch'ten sonra yapılır ve birleştirme aynı getirilen uca "git merge --ff-only @{u}" ile olur (= git pull --ff-only, arada yeni
fetch yok). Sonra .bat'lar yeniden üretilir (bat_yenile.py).
Güvenlik: anahtar dosyalarının içeriği hiçbir zaman açılmaz ya da yazdırılmaz (yalnız boyut ve tarih). Flow kilidi varken FLOW_GIRIS
Memmet'i açmaz (Memmet'in kendi ön koşulu). Kilidi yalnız UYARI_GECTI.bat (flow_yuk.py --uyari-gecti, şartlarıyla) kaldırır.
Çıkış kodları: 0 tamam · 1 HATA (ör. internet yok) · 2 KULLANICI (yerel değişiklik, anahtar yok) · 4 ORTAM (git/claude yok, ZIP, YOLLAR yok).
"""
import os, sys, json, time, shutil, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

TAMAM, HATA, KULLANICI, ORTAM = 0, 1, 2, 4
IZINLER = {"gece_flow": "Gece Flow (Memmet gece kendisi gönderir; aynı ya da daha yavaş tempo, uyarıda yine durur)",
           "gemini_api_ucretli": "Gemini API'nin ÜCRETLİ kullanımı (dolar tavanıyla)",
           "flow_kilitliyken_vertex": "Flow kilitliyken Vertex (resmî, ücretli; dolar tavanı > 0 da gerekir)",
           "cc0_efekt_indir": "CC0 ses efekti indirme (Freesound)",
           "youtube_baglanti": "YouTube bağlantısı (kanal verisi)",
           "yukleme": "YouTube'a yükleme (her film için ayrıca onay)"}
GEMINI_DOSYA = "gemini_anahtar.txt"
GEMINI_BILGI = ("Bilgi: Gemini API'nin ücretsiz katmanında Google gönderilen girdileri ürün geliştirmede kullanabilir (bellekten; "
                "Ö0-e'de doğrulanacak). Bu yüzden ücretsiz anahtarla yalnız filmin kendi dosyaları gönderilir.")


def _git(depo, *a, ag=False):
    """git komutu. Ağ isteyen komutta (fetch) Git Credential Manager penceresi açılabilir; öbürlerinde soru yok."""
    env = dict(os.environ, LC_ALL="C")
    if not ag: env["GIT_TERMINAL_PROMPT"] = "0"
    r = subprocess.run(["git", "-C", depo] + list(a), capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=600 if ag else 60, env=env)
    return r.returncode, r.stdout, r.stderr


def _z(s): return [x for x in s.split("\0") if x]


def guncelle_denetle(depo):
    """fetch + denetim. Dönüş {kod, durum, mesaj, gelen, cakisan}. Hiçbir dosyaya dokunmaz (yalnız .git/ içindeki uzak referanslar)."""
    if not os.path.exists(os.path.join(depo, ".git")):
        return dict(kod=ORTAM, durum="zip", mesaj="Bu set ZIP ile kurulmuş (.git yok); GUNCELLE kapalı. Güncellemek için "
                    "BASLA_BURADAN.txt'deki 'git clone' adımıyla yeniden kur (veri klasörün olduğu gibi kalır).")
    if not shutil.which("git"):
        return dict(kod=ORTAM, durum="git_yok", mesaj="git kurulu değil; GUNCELLE çalışamaz. git-scm.com'dan git'i kur, sonra tekrar dene.")
    k, o, _ = _git(depo, "status", "--porcelain=v1", "-z", "--untracked-files=no")
    if k != 0: return dict(kod=HATA, durum="git_hata", mesaj="git durumu okunamadı; hiçbir şey değiştirilmedi.")
    yerel = [x[3:] for x in _z(o)]
    if yerel:
        return dict(kod=KULLANICI, durum="yerel_degisiklik", yerel=yerel, mesaj=f"Sette {len(yerel)} dosyada yerel değişiklik var "
                    "(ör. " + yerel[0] + "); güncelleme yapılmadı, hiçbir dosya değişmedi. Claude'a 'GUNCELLE yerel değişiklik' de.")
    k, _, e = _git(depo, "fetch", "--quiet", ag=True)
    if k != 0: return dict(kod=HATA, durum="fetch", mesaj="Güncelleme indirilemedi (internet ya da GitHub girişi); hiçbir şey değişmedi.")
    k, ust, _ = _git(depo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if k != 0: return dict(kod=ORTAM, durum="ust_yok", mesaj="Bu dalın GitHub karşılığı yok; güncelleme yapılmadı.")
    k, o, _ = _git(depo, "rev-list", "--left-right", "--count", "HEAD...@{u}")
    ileri, geri = (int(x) for x in o.split()) if k == 0 else (0, 0)
    if ileri:
        return dict(kod=KULLANICI, durum="yerel_commit", mesaj=f"Sette {ileri} yerel kayıt (commit) var; güncelleme yapılmadı, hiçbir "
                    "dosya değişmedi. Claude'a 'GUNCELLE yerel commit' de.")
    if not geri: return dict(kod=TAMAM, durum="guncel", mesaj="Set zaten güncel.")
    k, o, _ = _git(depo, "diff", "--name-only", "-z", "HEAD", "@{u}")
    gelen = _z(o); onekler = set()
    for p in gelen:
        parca = p.split("/")
        onekler |= {"/".join(parca[:i]) for i in range(1, len(parca) + 1)}
    _, o, _ = _git(depo, "ls-files", "--others", "-z")          # izlenmeyen + yok sayılan (git yok sayılanı ezebilir)
    izsiz = _z(o); cakisan = sorted(p for p in izsiz if p.rstrip("/") in onekler or any(g.startswith(p.rstrip("/") + "/") for g in gelen))
    if cakisan:
        return dict(kod=KULLANICI, durum="izlenmeyen_cakisma", cakisan=cakisan, gelen=gelen,
                    mesaj=f"Güncelleme senin {len(cakisan)} dosyanın üzerine yazacaktı (ör. {cakisan[0]}); güncelleme yapılmadı, "
                          "hiçbir dosya değişmedi. Claude'a 'GUNCELLE çakışma' de.")
    return dict(kod=TAMAM, durum="hazir", gelen=gelen, geri=geri, ust=ust.strip(), mesaj=f"{geri} yeni kayıt var.")


def guncelle(depo=None, bat_yenile=True, yaz=print):
    depo = os.path.abspath(depo or _depo())
    d = guncelle_denetle(depo)
    if d["durum"] != "hazir": yaz(d["mesaj"]); return d["kod"]
    k, _, e = _git(depo, "merge", "--ff-only", "--quiet", "@{u}")
    if k != 0:
        yaz("Güncelleme uygulanamadı (git ileri sarma reddetti); setin durumu değişmedi. Claude'a haber ver."); return HATA
    yaz(f"Set güncellendi ({d['geri']} yeni kayıt, {len(d['gelen'])} dosya).")
    if bat_yenile:
        p = (ortak.json_oku(ortak.yollar_dosyasi(), {}) or {}).get("python", {}).get("ana") or sys.executable
        subprocess.call([p, os.path.join(depo, "YZ_FILM", "ARACLAR", "bat_yenile.py")])
    return TAMAM


def _depo():
    try: return ortak.yollar().get("depo_kok") or ortak.DEPO_KOK
    except ortak.YolYok: return ortak.DEPO_KOK


# ---------------------------------------------------------------- izinler (FILM_AYAR.json; yalnız izin, tercih, para tavanı)
def ayar_yolu(): return os.path.join(ortak.yollar()["ayarlar"], "FILM_AYAR.json")


def izin_oku():
    import kurulum
    return kurulum.film_ayar_birlestir(ortak.json_oku(ayar_yolu(), {}) or {})


def izin_degistir(ac=(), kapat=(), usd=None, mod=None):
    a = izin_oku()
    for ad in list(ac) + list(kapat):
        if ad not in IZINLER: raise ValueError(f"bilinmeyen izin: {ad} (olanlar: {', '.join(IZINLER)})")
    for ad in ac: a["izinler"][ad] = True
    for ad in kapat: a["izinler"][ad] = False
    if usd is not None:
        usd = float(usd)
        if usd < 0: raise ValueError("dolar tavanı negatif olamaz")
        a["butce"]["usd_tavan_film"] = int(usd) if usd == int(usd) else usd
    if mod is not None:
        if mod not in ("tam_otomatik", "onayli"): raise ValueError("mod: tam_otomatik | onayli")
        a["mod"] = mod
    ortak.atomik_yaz(ayar_yolu(), a)
    return a


def izin_metni(a):
    s = [f"İZİNLER (varsayılan hepsi kapalı; yalnız sen açarsın) · mod: {a['mod']} · film başına dolar tavanı: "
         f"{a['butce']['usd_tavan_film']}"]
    for i, (ad, ac) in enumerate(IZINLER.items(), 1): s.append(f"  {i}. [{'AÇIK ' if a['izinler'].get(ad) else 'kapalı'}] {ac}")
    if a["izinler"].get("flow_kilitliyken_vertex") and not a["butce"]["usd_tavan_film"]:
        s.append("  Not: Flow kilitliyken Vertex için dolar tavanı da 0'dan büyük olmalı; şu an kullanılmaz.")
    return "\n".join(s)


def izinler(a):
    if "--goster" in a or any(x in a for x in ("--ac", "--kapat", "--usd", "--mod")):
        g = lambda k: [a[i + 1] for i, x in enumerate(a) if x == k and i + 1 < len(a)]
        if "--goster" not in a:
            izin_degistir(g("--ac"), g("--kapat"), (g("--usd") or [None])[-1], (g("--mod") or [None])[-1])
        print(izin_metni(izin_oku())); return TAMAM
    if not (sys.stdin and sys.stdin.isatty()): print(izin_metni(izin_oku())); return TAMAM
    adlar = list(IZINLER)
    while True:      # kullanıcının kendi açtığı panel: burada seçim yapmak onun isteğidir (KK1 soru kuralı dışında)
        print("\n" + izin_metni(izin_oku()))
        c = input("Değiştirmek istediğin numarayı yaz (d = dolar tavanı, m = onaylı/tam otomatik, Enter = çık): ").strip().lower()
        if not c: return TAMAM
        try:
            if c == "d": izin_degistir(usd=input("Film başına dolar tavanı (0 = harcama yok): ").strip().replace(",", "."))
            elif c == "m": izin_degistir(mod="onayli" if izin_oku()["mod"] == "tam_otomatik" else "tam_otomatik")
            elif c.isdigit() and 1 <= int(c) <= len(adlar):
                ad = adlar[int(c) - 1]
                izin_degistir(**({"kapat": [ad]} if izin_oku()["izinler"].get(ad) else {"ac": [ad]}))
            else: print("Anlaşılmadı.")
        except ValueError as e: print("!!", e)


# ---------------------------------------------------------------- Gemini anahtarı (içerik okunmaz)
def dosya_durumu(yol):
    """Anahtar dosyası: var mı, boş mu (yalnız boyut), tarih. İçerik AÇILMAZ (kurulum.dosya_durumu)."""
    import kurulum
    return kurulum.dosya_durumu(yol)


def gemini_test(sahte=False, yaz=print):
    y = ortak.yollar(); yol = os.path.join(y["ayarlar"], GEMINI_DOSYA)
    os.makedirs(y["ayarlar"], exist_ok=True)
    if not os.path.exists(yol): open(yol, "w", encoding="utf-8").close()
    d = dosya_durumu(yol); ortamda = bool(os.environ.get("GEMINI_API_KEY"))
    var = d["dolu"] or ortamda
    sonuc = {"_surum": 1, "zaman": time.strftime("%Y-%m-%d %H:%M:%S"), "anahtar_var": var, "dosya_tarihi": d["tarih"],
             "kaynak": "dosya" if d["dolu"] else ("ortam" if ortamda else None),
             "gemini_katman": "ucretsiz" if (sahte and var) else "bilinmiyor", "sahte": sahte,
             "olculemedi": not sahte, "neden": None if sahte else "ücretsiz katman ve video/ses girişi Ö0-e'de sınanır (olcum0/gemini_deneme.py)"}
    ortak.atomik_yaz(os.path.join(y["ayarlar"], "GEMINI_DURUMU.json"), sonuc)
    if not var:
        yaz(f"Gemini anahtarı yok: {yol} boş. Google AI Studio'da (faturalandırma açmadan) ücretsiz bir API anahtarı al, bu dosyanın ilk "
            "satırına yapıştır, kaydet ve GEMINI_TEST.bat'a yeniden çift tıkla.")
        return KULLANICI
    yaz(f"Gemini anahtarı bulundu ({'dosya, ' + d['tarih'] if d['dolu'] else 'ortam değişkeni'}; içeriği okunmadı, yazdırılmadı). "
        "Filmi yayından önce bir 'kulak' (dinleyici) ve 'göz' (izleyici) dinleyecek.")
    yaz("Ücretsiz katman: " + ("sahte deneme, ücretsiz sayıldı." if sahte else "ÖLÇÜLEMEDİ — ilk ölçüm turunda (Ö0-e) sınanacak."))
    yaz(GEMINI_BILGI)
    return TAMAM


# ---------------------------------------------------------------- film klasörü işleri
def durdur(film, yaz=print):
    film = os.path.abspath(film)
    ortak.atomik_yaz(os.path.join(film, "DUR"), {"zaman": time.strftime("%Y-%m-%d %H:%M:%S"), "kaynak": "DURDUR.bat"})
    yaz("Film durduruldu: set yeni iş başlatmaz. Açık bir Memmet penceresi varsa kapatabilirsin. Sürdürmek için DEVAM.bat.")
    return TAMAM


def devam(film, yaz=print):
    film = os.path.abspath(film); p = os.path.join(film, "DUR")
    if os.path.exists(p):
        h = os.path.join(film, "_ESKI", time.strftime("DUR_%Y%m%d_%H%M%S")); os.makedirs(os.path.dirname(h), exist_ok=True)
        shutil.move(p, h)
    if not shutil.which("claude"): yaz(CLAUDE_YOK); return ORTAM
    yaz("Film sürüyor: Claude Code açılıyor ve 'devam' yazıyor. Açılmazsa Masaüstündeki FILM_SETI.bat'a çift tıklayıp 'devam' yaz.")
    return TAMAM


CLAUDE_YOK = ("Claude Code bulunamadı. Claude Code'u kur (claude.ai/code), bu pencereyi kapat ve FILM_SETI.bat'a yeniden çift tıkla.")


def film_seti(yaz=print):
    try: ortak.yollar()
    except ortak.YolYok: yaz("Set henüz kurulmamış: önce setin klasöründeki KURULUM.bat'a çift tıkla."); return ORTAM
    if not shutil.which("claude"): yaz(CLAUDE_YOK); return ORTAM
    yaz("Film seti açılıyor. Aktif film varsa kaldığı yerden sürer; yoksa yalnız filmin konusunu yaz.")
    return TAMAM


def flow_giris_komutu():
    """Memmet'in --giris kipi için hesap düzeyinde boş bir v1 kök kurar (<veri>/HESAP/FLOW_GIRIS) ve komutu döndürür."""
    y = ortak.yollar(); kok = os.path.join(y["hesap"], "FLOW_GIRIS")
    if not os.path.exists(os.path.join(kok, "SAHNELER.json")):
        ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), {"film": "FLOW_GIRIS", "karakterler": {}, "sahneler": []})
    p = (y.get("python") or {}).get("ana") or sys.executable
    return [p, os.path.join(ortak.ARACLAR, "memmet.py"), kok, "--giris"]


def flow_giris(kuru=False, yaz=print):
    k = flow_giris_komutu()
    yaz("Memmet'in Chrome'u açılacak. Flow'a kendi Google hesabınla bir kez giriş yap (başka hesap kullanma). "
        "'Ben robot değilim' çıkarsa kendin çöz. Bitince pencereyi kapatabilirsin.")
    if kuru: return TAMAM
    return subprocess.call(k)


def film_deneme(film):
    y = ortak.yollar(); p = (y.get("python") or {}).get("ana") or sys.executable
    print("Kredisiz deneme: sahte görsel/video/ses ile hat deneniyor.", flush=True)
    return subprocess.call([p, os.path.join(ortak.ARACLAR, "film.py"), os.path.abspath(film), "--saglayici", "sahte"])


def main(a=None):
    a = sys.argv[1:] if a is None else list(a)
    if not a: print(__doc__); return ORTAM
    k, r = a[0], a[1:]
    arg = lambda: r[0] if r and not r[0].startswith("--") else None
    try:
        if k == "film-seti": return film_seti()
        if k == "guncelle": return guncelle(r[r.index("--depo") + 1] if "--depo" in r else None)
        if k == "flow-giris": return flow_giris("--kuru" in r)
        if k == "izinler": return izinler(r)
        if k == "gemini-test": return gemini_test("sahte" in r)
        if k in ("durdur", "devam", "film-deneme") and arg():
            return {"durdur": durdur, "devam": devam, "film-deneme": film_deneme}[k](arg())
    except ortak.YolYok as e: print("!!", e); return ORTAM
    except ValueError as e: print("!!", e); return HATA
    print(__doc__); return ORTAM


if __name__ == "__main__":
    sys.exit(main())
