"""VERİ EMNİYETİ — masaüstündeki eski YZ_FILM klasöründe (veri kökü) yamasız Memmet'e giden giriş noktalarını emekliye ayırır (D-02).

  python kurulum.py --veri-emniyet [--veri <klasör>]      (ya da doğrudan: python veri_emniyet.py [<klasör>])

Taşınanlar (_ESKI/<tarih>/ altına; HİÇBİR ŞEY SİLİNMEZ):
  eski memmet*.py / _memmet_yedek_*.py, veri kökünün ARACLAR/film.py'si, Memmet'i çağıran bütün .bat/.cmd/.ps1'ler
  (film klasörlerindeki MEMMET_*, FILM_HATTI, CAPCUT_PROJESI_OLUSTUR, gece_video.ps1, memmet_dongu.ps1 ...),
  veri kökündeki BASLA_BURADAN.txt, 00_BENI_OKU.txt, KURULUM.bat, YENI_FILM.bat.
Yerlerine: "bu dosya emekli" .bat/.ps1/notu; memmet.py yerine depodaki yamalı Memmet'i mutlak yolla çağıran sarmalayıcı;
5 satırlık CLAUDE.md. OpenMontage, GELISTIRME, memmet_profil ve _ESKI klasörlerine dokunulmaz.
Rapor: <veri>/_ESKI/EMNIYET_RAPORU.json ("kalan_giris_noktasi" boş olmalı). Tekrar çalıştırmak güvenlidir.
"""
import os, sys, re, json, time, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

SARMALAYICI_IMI = "# YZ_FILM_SET memmet sarmalayicisi"
DOKUNMA = {"_ESKI", "OpenMontage", "GELISTIRME", "AYARLAR", "memmet_profil", "__pycache__", ".git"}   # AYARLAR: anahtar dosyaları okunmaz
KOK_DOSYALARI = ("BASLA_BURADAN.txt", "00_BENI_OKU.txt", "KURULUM.bat", "YENI_FILM.bat")
BETIK_UZANTI = (".bat", ".cmd", ".ps1")
MEMMET_IZI = re.compile(r"memmet[\w\-]*\.py|memmet_dongu|gece_video|film\.py", re.I)
EMEKLI_IMI = "Bu dosya emekli"
EMEKLI_BAT = ("@echo off\r\necho.\r\necho Bu dosya emekli. Masaustundeki FILM_SETI.bat'i kullan.\r\n"
              "echo (Eski hali _ESKI klasorunde duruyor; silinmedi.)\r\npause\r\n")
EMEKLI_PS1 = "Write-Host \"Bu dosya emekli. Masaustundeki FILM_SETI.bat'i kullan. (Eski hali _ESKI klasorunde.)\"\r\n"
VERI_CLAUDE = """# BU KLASÖR FİLM SETİNİN VERİ KLASÖRÜDÜR
Set burada çalışmaz; burada kod değiştirme, Memmet'i çalıştırma, dosya silme.
Kullanıcıya yalnız şunu söyle: "Masaüstündeki FILM_SETI.bat'a çift tıkla; Claude doğru klasörde açılır."
Başka bir şey yapma.
(Bu dosyayı kurulum.py --veri-emniyet yazdı.)
"""
SARMALAYICI = '''{imi}
"""Eski Memmet emekli. Bu dosya depodaki yamalı Memmet'i çağırır (Flow uyarısında her kipte durur)."""
import os, sys, subprocess
DEPO_MEMMET = {depo!r}
VERI = {veri!r}
if __name__ == "__main__":
    if not os.path.exists(DEPO_MEMMET):
        print("Yamalı Memmet bulunamadı:", DEPO_MEMMET, "- Claude'a haber ver."); sys.exit(4)
    sys.exit(subprocess.call([sys.executable, DEPO_MEMMET] + sys.argv[1:], env=dict(os.environ, YZ_FILM_VERI=VERI)))
'''


def varsayilan_veri(): return os.path.join(os.path.expanduser("~"), "Desktop", "YZ_FILM")


def _oku(yol, n=None):
    try:
        with open(yol, encoding="utf-8", errors="replace") as f: return f.read(n) if n else f.read()
    except OSError: return ""


def _bizim_mi(yol):
    """Bu aracın koyduğu sarmalayıcı / emeklilik dosyası mı (yeniden taşınmaz)."""
    m = _oku(yol, 600)
    return m.startswith(SARMALAYICI_IMI) or (EMEKLI_IMI in m and len(m) < 500)


def tara(veri):
    """Taşınacaklar: [(göreli yol, neden)]."""
    out = []
    for kok, dirs, files in os.walk(veri):
        dirs[:] = [d for d in dirs if d not in DOKUNMA]
        for f in files:
            yol = os.path.join(kok, f); rel = os.path.relpath(yol, veri); alt = f.lower()
            if _bizim_mi(yol): continue
            if alt.endswith(".py") and (alt.startswith("memmet") or alt.startswith("_memmet_yedek")):
                out.append((rel, "eski Memmet"))
            elif alt == "film.py" and rel.replace("\\", "/") == "ARACLAR/film.py":
                out.append((rel, "eski film.py (onay ve kapıları atlıyor)"))
            elif alt.endswith(BETIK_UZANTI) and MEMMET_IZI.search(_oku(yol)):
                out.append((rel, "Memmet'i / eski hattı çağıran betik"))
            elif kok == veri and f in KOK_DOSYALARI:
                out.append((rel, "veri kökündeki eski giriş belgesi/betiği"))
    return sorted(out)


def _yerine_koy(yol, hedef_rel, depo_memmet, veri):
    f = os.path.basename(yol).lower()
    if f == "memmet.py":
        open(yol, "w", encoding="utf-8").write(SARMALAYICI.format(imi=SARMALAYICI_IMI, depo=depo_memmet, veri=veri))
        return "yamalı Memmet sarmalayıcısı"
    if f.endswith((".bat", ".cmd")): open(yol, "w", encoding="ascii", newline="").write(EMEKLI_BAT); return "emeklilik .bat'ı"
    if f.endswith(".ps1"): open(yol, "w", encoding="utf-8", newline="").write(EMEKLI_PS1); return "emeklilik .ps1'i"
    if f.endswith(".txt"):
        open(yol, "w", encoding="utf-8").write(f"{EMEKLI_IMI}. Masaüstündeki FILM_SETI.bat'a çift tıkla.\nEski hali: {hedef_rel}\n")
        return "emeklilik notu"
    return None   # film.py, _memmet_yedek_*.py: yerine bir şey konmaz


def veri_emniyet(veri=None, depo_araclar=HERE, sessiz=False):
    """Veri kökünü emniyete alır ve raporu döndürür. durum: temiz | veri_yok | KALAN_VAR."""
    if not veri:
        try:
            import ortak; veri = ortak.yollar()["veri_kok"]
        except Exception: veri = os.environ.get("YZ_FILM_VERI") or varsayilan_veri()
    veri = os.path.abspath(veri)
    yaz = (lambda *a: None) if sessiz else (lambda *a: print(*a, flush=True))
    rapor = {"veri": veri, "zaman": time.strftime("%Y-%m-%d %H:%M:%S"), "tasinan": [], "konan": [], "kalan_giris_noktasi": []}
    if not os.path.isdir(veri):
        yaz(f"  Veri kökü yok ({veri}); emniyete alınacak bir şey yok."); rapor["durum"] = "veri_yok"; return rapor
    if os.path.abspath(veri) == os.path.abspath(os.path.dirname(depo_araclar)):
        raise SystemExit("Bu klasör deponun kendisi, veri kökü değil. --veri ile Masaüstü\\YZ_FILM'i ver.")
    eski = os.path.join(veri, "_ESKI", time.strftime("%Y%m%d_%H%M%S"))
    depo_memmet = os.path.join(os.path.abspath(depo_araclar), "memmet.py")
    for rel, neden in tara(veri):
        kaynak = os.path.join(veri, rel); hedef = os.path.join(eski, rel); hedef_rel = os.path.relpath(hedef, veri)
        os.makedirs(os.path.dirname(hedef), exist_ok=True)
        shutil.move(kaynak, hedef)
        rapor["tasinan"].append({"dosya": rel, "neden": neden, "nereye": hedef_rel})
        yaz(f"  taşındı: {rel}  ({neden}) → {hedef_rel}")
        konan = _yerine_koy(kaynak, hedef_rel, depo_memmet, veri)
        if konan: rapor["konan"].append({"dosya": rel, "ne": konan})
    cm = os.path.join(veri, "CLAUDE.md")
    if os.path.exists(cm) and _oku(cm) != VERI_CLAUDE:
        hedef = os.path.join(eski, "CLAUDE.md"); os.makedirs(eski, exist_ok=True); shutil.move(cm, hedef)
        rapor["tasinan"].append({"dosya": "CLAUDE.md", "neden": "eski CLAUDE.md", "nereye": os.path.relpath(hedef, veri)})
    if not os.path.exists(cm):
        open(cm, "w", encoding="utf-8").write(VERI_CLAUDE); rapor["konan"].append({"dosya": "CLAUDE.md", "ne": "veri kökü yönlendirmesi"})
    rapor["kalan_giris_noktasi"] = [rel for rel, _ in tara(veri)]
    rapor["durum"] = "temiz" if not rapor["kalan_giris_noktasi"] else "KALAN_VAR"
    os.makedirs(os.path.join(veri, "_ESKI"), exist_ok=True)
    with open(os.path.join(veri, "_ESKI", "EMNIYET_RAPORU.json"), "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=1)
    yaz(f"  {len(rapor['tasinan'])} dosya _ESKI'ye taşındı (silinmedi). Yamasız Memmet'e giden giriş noktası: "
        f"{len(rapor['kalan_giris_noktasi'])}")
    return rapor


if __name__ == "__main__":
    r = veri_emniyet(sys.argv[1] if len(sys.argv) > 1 else None)
    sys.exit(0 if r["durum"] in ("temiz", "veri_yok") else 3)
