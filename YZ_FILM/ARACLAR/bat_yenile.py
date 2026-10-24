"""BAT YENİLE — kullanıcının çift tıkladığı bütün .bat dosyalarını üretir (TASARIM §6.9, §5.6 yol göçü, [SON] O-1, O-5).

Kullanım:
  python bat_yenile.py                       depo kökü .bat'ları + masaüstündeki FILM_SETI.bat + her film klasörünün .bat'ları
  python bat_yenile.py --depo-koku           yalnız depo kökü (+ masaüstü FILM_SETI.bat)
  python bat_yenile.py --film <klasör>       yalnız o film klasörünün .bat'ları
  python bat_yenile.py --kuru                hiçbir şey yazmaz; ne yazılacağını listeler
  Kodda: import bat_yenile as by; by.depo_batlari() · by.film_batlari() · by.yenile(...) · by.bat_yaz(yol, icerik, eski_kok)

Kurallar (kabul: test_kurulum, test_yollar):
  - Her .bat ASCII + CRLF; başı "@echo off", "chcp 65001", bir "rem yz_film_set:bat_yenile" imi; tek iş yapar.
  - Python'u VE betiği MUTLAK yolla çağırır (YOLLAR.json → python.ana, ortak.ARACLAR). Göreli "..\\..\\ARACLAR" asla yok.
  - Türkçe mesajı .bat yazmaz, Python yazar (bat_isleri.py); .bat'ta yalnız ASCII komut vardır. Yol ASCII dışı harf içeriyorsa
    (ör. kullanıcı adı) dosya UTF-8 yazılır (chcp 65001 bunu okur) ve rapora not düşülür.
  - Veri kökündeki .bat'lar memmet*.py ya da film.py'yi doğrudan anmaz (veri_emniyet onları eski giriş noktası sayar); bu işleri
    bat_isleri.py'nin alt komutları yapar.
  - Var olan bir .bat bu aracın imini taşımıyorsa ve içeriği farklıysa üzerine yazılmadan önce <veri>/_ESKI/bat_yenile_<zaman>/'a
    taşınır (silinmez). İmli dosya yeniden üretilir.
  - Depo kökündeki KURULUM.bat depoya işlenmiş sabit önyükleyicidir; bu araç ona dokunmaz (değişirse GUNCELLE.bat yerel değişiklik görür).
    Burada üretilen depo kökü .bat'ları makineye özgüdür ve git'e girmez (.gitignore).
Çıkış kodları: 0 tamam · 1 yazılamadı · 4 YOLLAR.json yok (önce KURULUM.bat).
"""
import os, sys, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

IM = "rem yz_film_set:bat_yenile"
YASAK = "..\\..\\ARACLAR"
DEPO_KOKU = ("FILM_SETI.bat", "GUNCELLE.bat", "FLOW_GIRIS.bat", "IZINLER.bat", "UYARI_GECTI.bat", "GEMINI_TEST.bat")
FILM_KLASORU = ("DEVAM.bat", "DURDUR.bat", "KONTROL.bat", "NOTLARI_OKU.bat", "FILM_DENEME_SAHTE.bat")
SABIT = ("KURULUM.bat",)          # depoya işlenmiş; üretilmez


def _bat(yol): return yol.replace("%", "%%")          # .bat içinde % kaçışı


def _metin(ad, satirlar, cd):
    bas = ["@echo off", f"{IM} {ad}", "chcp 65001 >nul", "title YZ FILM SETI - " + ad[:-4].replace("_", " ")]
    if cd: bas.append(f'cd /d {cd}')
    return "\r\n".join(bas + list(satirlar)) + "\r\n"


def _kaynaklar(python=None, araclar=None, depo=None):
    if python is None or depo is None:
        y = ortak.yollar(); python = python or (y.get("python") or {}).get("ana") or sys.executable
        depo = depo or y.get("depo_kok") or ortak.DEPO_KOK
    return os.path.abspath(python), os.path.abspath(araclar or ortak.ARACLAR), os.path.abspath(depo)


def _cagir(python, araclar):
    def c(betik, *arg):
        return " ".join([f'"{_bat(python)}"', f'"{_bat(os.path.join(araclar, betik))}"'] + list(arg))
    return c


def depo_batlari(python=None, araclar=None, depo=None):
    """Depo kökü .bat'ları {ad: içerik}. FILM_SETI.bat masaüstüne de kopyalanır (her yerden aynı klasörde açılır)."""
    python, araclar, depo = _kaynaklar(python, araclar, depo)
    c = _cagir(python, araclar); bi = lambda *a: c("bat_isleri.py", *a)
    dur = "pause"
    return {
        "FILM_SETI.bat": _metin("FILM_SETI.bat", [bi("film-seti"), "if errorlevel 1 (", "  pause", "  exit /b 4", ")", "claude"],
                                f'"{_bat(depo)}"'),
        "GUNCELLE.bat": _metin("GUNCELLE.bat", [bi("guncelle"), dur], '"%~dp0"'),
        "FLOW_GIRIS.bat": _metin("FLOW_GIRIS.bat", [bi("flow-giris"), dur], '"%~dp0"'),
        "IZINLER.bat": _metin("IZINLER.bat", [bi("izinler"), dur], '"%~dp0"'),
        "UYARI_GECTI.bat": _metin("UYARI_GECTI.bat", [c("flow_yuk.py", "--uyari-gecti"), dur], '"%~dp0"'),
        "GEMINI_TEST.bat": _metin("GEMINI_TEST.bat", [bi("gemini-test"), dur], '"%~dp0"'),
    }


def film_batlari(python=None, araclar=None, depo=None):
    """Film klasörü .bat'ları {ad: içerik}; film klasörü "%~dp0." ile verilir. DEVAM Claude Code'u depo klasöründe sürdürür."""
    python, araclar, depo = _kaynaklar(python, araclar, depo)
    c = _cagir(python, araclar); bi = lambda *a: c("bat_isleri.py", *a); f = '"%~dp0."'
    return {
        "DEVAM.bat": _metin("DEVAM.bat", [bi("devam", f), "if errorlevel 1 (", "  pause", "  exit /b 4", ")",
                                          f'cd /d "{_bat(depo)}"', 'claude --continue "devam"'], None),
        "DURDUR.bat": _metin("DURDUR.bat", [bi("durdur", f), "pause"], None),
        "KONTROL.bat": _metin("KONTROL.bat", [c("kontrol.py", f), "pause"], None),
        "NOTLARI_OKU.bat": _metin("NOTLARI_OKU.bat", [c("notlari_oku.py", f), "pause"], None),
        "FILM_DENEME_SAHTE.bat": _metin("FILM_DENEME_SAHTE.bat", [bi("film-deneme", f), "pause"], None),
    }


def kodla(icerik):
    """ASCII; olmazsa UTF-8 (chcp 65001). (bayt, ascii_mi)"""
    try: return icerik.encode("ascii"), True
    except UnicodeEncodeError: return icerik.encode("utf-8"), False


def denetle(icerik):
    """Kural ihlalleri listesi (boşsa geçer): CRLF, göreli ARACLAR, im."""
    h = []
    if YASAK in icerik or "../../ARACLAR" in icerik: h.append("göreli ..\\..\\ARACLAR yolu")
    if "\n" in icerik.replace("\r\n", ""): h.append("CRLF değil")
    if IM not in icerik: h.append("bat_yenile imi yok")
    return h


def bat_yaz(yol, icerik, eski_kok=None):
    """.bat'ı yazar. İmsiz ve farklı bir dosya varsa önce eski_kok'a taşınır (silinmez). Dönüş: yazildi | ayni | tasindi_yazildi."""
    h = denetle(icerik)
    if h: raise ValueError(f"{os.path.basename(yol)}: " + ", ".join(h))
    b, _ = kodla(icerik); durum = "yazildi"
    if os.path.exists(yol):
        with open(yol, "rb") as f: eski = f.read()
        if eski == b: return "ayni"
        if IM.encode() not in eski:
            hedef_kok = eski_kok or os.path.join(os.path.dirname(yol), "_ESKI")
            hedef = os.path.join(hedef_kok, time.strftime("bat_yenile_%Y%m%d_%H%M%S"), os.path.basename(yol))
            os.makedirs(os.path.dirname(hedef), exist_ok=True); shutil.move(yol, hedef); durum = "tasindi_yazildi"
    os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
    tmp = yol + ".tmp"
    with open(tmp, "wb") as f: f.write(b)
    os.replace(tmp, yol)
    return durum


def film_klasorleri(filmler):
    if not os.path.isdir(filmler): return []
    out = []
    for ad in sorted(os.listdir(filmler)):
        d = os.path.join(filmler, ad)
        if ad.startswith(("_", ".")) or not os.path.isdir(d): continue
        if any(os.path.exists(os.path.join(d, x)) for x in ("SAHNELER.json", "FILM_DURUM.json", "00_KONU.md")): out.append(d)
    return out


def yenile(depo=None, veri=None, masaustu=None, depo_koku=True, filmler=True, film=None, kuru=False, python=None, araclar=None,
           yaz=print):
    """Bütün .bat'ları üretir. Rapor: {"yazilan": [{yol, durum, ascii}], "kuru": bool}."""
    y = ortak.yollar()
    depo = os.path.abspath(depo or y.get("depo_kok") or ortak.DEPO_KOK); veri = os.path.abspath(veri or y["veri_kok"])
    masaustu = masaustu if masaustu is not None else (y.get("masaustu") or os.path.dirname(veri))
    eski = os.path.join(veri, "_ESKI"); r = {"yazilan": [], "kuru": kuru}
    isler = []
    if depo_koku:
        for ad, ic in depo_batlari(python, araclar, depo).items():
            isler.append((os.path.join(depo, ad), ic))
            if ad == "FILM_SETI.bat" and masaustu and os.path.isdir(masaustu) and os.path.abspath(masaustu) != depo:
                isler.append((os.path.join(masaustu, ad), ic))
    hedef_filmler = [os.path.abspath(film)] if film else (film_klasorleri(y["filmler"]) if filmler else [])
    if hedef_filmler:
        fb = film_batlari(python, araclar, depo)
        for d in hedef_filmler: isler += [(os.path.join(d, ad), ic) for ad, ic in fb.items()]
    for yol, ic in isler:
        asc = kodla(ic)[1]
        durum = "kuru" if kuru else bat_yaz(yol, ic, eski)
        r["yazilan"].append({"yol": yol, "durum": durum, "ascii": asc})
        if durum not in ("ayni",):
            yaz(f"  {'yazılacak' if kuru else durum}: {yol}" + ("" if asc else "  (yolda Türkçe harf var: UTF-8 yazıldı)"))
    return r


def main(a=None):
    a = sys.argv[1:] if a is None else list(a)
    try:
        film = a[a.index("--film") + 1] if "--film" in a else None
        r = yenile(film=film, depo_koku=film is None, filmler=film is None and "--depo-koku" not in a, kuru="--kuru" in a)
    except ortak.YolYok as e: print("!!", e); return 4
    except (OSError, ValueError) as e: print("!! .bat yazılamadı:", e); return 1
    print(f".bat dosyaları {'listelendi' if r['kuru'] else 'hazır'}: {len(r['yazilan'])} dosya.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
