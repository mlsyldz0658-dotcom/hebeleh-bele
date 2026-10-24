"""DERS YEDEĞİ — ders defterinin ve ortak yedek kopyasının aracı (TASARIM D-33, D-42, [SON] O-6, §1.3 A18 ve A00).

`ders_defteri.py --yedekle` bu modülü çağırır (bağlantı satırı: paylaşılan istek); `evren.py --yedekle` aynı kopya işlevini kullanır.
Kullanım:
  python ders_yedekle.py [--hedef <yedek kökü>]     <veri>/BILGI/DERSLER/ + KURALLAR_OGRENILEN.json + DERSLER_AKTIF.md
                                                    → <yedek>/DERSLER/ (+ SHA1_LISTESI.json)
  python ders_yedekle.py --dogrula [--yenile]       yedeğin sha1 listesini kaynakla karşılaştırır; fark bilgi olarak yazılır,
                                                    --yenile ile yedek yeniden alınır (A00)
Kodda:
  kopya_yedek(kaynak_dizin, hedef, ekler={rel: mutlak}) → {durum, kopyalanan, dogrulanan, fark, hedef}
  sha1_listesi(kok) → {rel: sha1} · liste_fark(kaynak_listesi, yedek_listesi) → [{dosya, neden}] · surucu_var(yol)
Kurallar (öğrenmeyle ya da ayarla gevşemez):
  - YALNIZ KOPYA: Windows'ta `robocopy /E` (/MIR ve /MOVE yok), başka yerde shutil.copy2. Hedefte fazladan dosya SİLİNMEZ.
  - AYARLAR klasörü ve *.tmp asla yedeğe girmez (anahtar dosyaları okunmaz da).
  - Yedek kökü ortak.yollar()["yedek"] (Windows'ta D:\\YZ_FILM_YEDEK). Sürücü takılı değilse BEKLE yok: bilgi + <veri>/HESAP/YEDEK_DURUMU.json
    "ertelendi"; yedek sonraki filmin A00'ında yeniden denenir (evren.py --yedek-dogrula).
  - Kopyadan sonra her dosyanın sha1'i yedekte yeniden ölçülür; uyuşmazlık HATA'dır (çıkış 1).
Çıkış kodları: 0 tamam ya da ertelendi · 1 kopya/sha1 hatası · 4 ORTAM (YOLLAR.json yok) · kullanım hatası 4.
"""
import os, sys, json, shutil, hashlib, datetime, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "ders_yedekle 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
LISTE_ADI = "SHA1_LISTESI.json"
HARIC_KLASOR = ("AYARLAR", "__pycache__")
HARIC_UZANTI = (".tmp",)


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def ortam(): return os.environ.get("YZ_FILM_ORTAM") or ("yerel" if os.name == "nt" else "bulut")


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""): h.update(parca)
    return h.hexdigest()


def _haric(rel):
    parcalar = rel.replace("\\", "/").split("/")
    return any(x in HARIC_KLASOR for x in parcalar) or rel.endswith(HARIC_UZANTI) or parcalar[-1] == LISTE_ADI


def sha1_listesi(kok):
    """{göreli posix yol: sha1} (AYARLAR, *.tmp ve sha1 listesinin kendisi hariç)."""
    out = {}
    if not os.path.isdir(kok): return out
    for d, alt, dosyalar in os.walk(kok):
        alt[:] = sorted(x for x in alt if x not in HARIC_KLASOR)
        for a in sorted(dosyalar):
            p = os.path.join(d, a); rel = os.path.relpath(p, kok).replace("\\", "/")
            if not _haric(rel): out[rel] = sha1(p)
    return out


def liste_fark(kaynak, yedek):
    """Kaynakta olup yedekte olmayan ya da farklı olan dosyalar (yedekte fazlası fark sayılmaz; silme yok)."""
    f = []
    for rel, s in sorted(kaynak.items()):
        if rel not in yedek: f.append({"dosya": rel, "neden": "yedekte yok"})
        elif yedek[rel] != s: f.append({"dosya": rel, "neden": "sha1 farklı"})
    return f


def surucu_var(yol):
    """Yedek kökünün sürücüsü takılı mı? Windows: 'D:\\' var mı. Başka yerde: üst klasör var mı (testler böyle benzetir)."""
    yol = os.path.abspath(yol)
    if os.name == "nt":
        s = os.path.splitdrive(yol)[0]
        return os.path.isdir(s + "\\") if s else True
    return os.path.isdir(os.path.dirname(yol))


def _robocopy(kaynak, hedef):
    """robocopy /E (kopya; /MIR, /MOVE, /PURGE YOK). Çıkış < 8 başarıdır."""
    komut = ["robocopy", kaynak, hedef, "/E", "/COPY:DAT", "/R:1", "/W:1", "/XD", *HARIC_KLASOR, "/XF", "*.tmp", LISTE_ADI,
             "/NP", "/NFL", "/NDL", "/NJH", "/NJS"]
    assert not any(x.upper() in ("/MIR", "/MOVE", "/PURGE", "/MOV") for x in komut)
    r = subprocess.run(komut, capture_output=True, text=True)
    return r.returncode < 8, r.returncode


def _python_kopya(kaynak, hedef, liste):
    n = 0
    for rel, s in liste.items():
        a, b = os.path.join(kaynak, rel), os.path.join(hedef, rel)
        if os.path.isfile(b) and sha1(b) == s: continue
        os.makedirs(os.path.dirname(b), exist_ok=True)
        tmp = b + ".tmp"; shutil.copy2(a, tmp); os.replace(tmp, b); n += 1
    return n


def kopya_yedek(kaynak, hedef, ekler=None, robocopy=None, kok=None):
    """kaynak klasörünü (+ ekler {yedekteki rel: mutlak dosya}) hedefe KOPYALAR, sha1 ile doğrular, SHA1_LISTESI.json yazar.
    kok: sürücü denetiminin yapıldığı yedek kökü (verilmezse hedef)."""
    kaynak, hedef = os.path.abspath(kaynak), os.path.abspath(hedef)
    if not surucu_var(kok or hedef):
        return {"durum": "ertelendi", "hedef": hedef, "neden": "yedek sürücüsü takılı değil", "kopyalanan": 0, "dogrulanan": 0, "fark": []}
    liste = sha1_listesi(kaynak)
    ekler = {k.replace("\\", "/"): v for k, v in (ekler or {}).items() if v and os.path.isfile(v)}
    os.makedirs(hedef, exist_ok=True)
    kullan_robo = (os.name == "nt" and shutil.which("robocopy")) if robocopy is None else robocopy
    if kullan_robo and liste:
        ok, kod = _robocopy(kaynak, hedef)
        if not ok: return {"durum": "hata", "hedef": hedef, "neden": f"robocopy çıkış {kod}", "kopyalanan": 0, "dogrulanan": 0, "fark": []}
        n = len(liste)
    else:
        n = _python_kopya(kaynak, hedef, liste)
    for rel, p in ekler.items():
        s = sha1(p); liste[rel] = s; b = os.path.join(hedef, rel)
        if not (os.path.isfile(b) and sha1(b) == s):
            os.makedirs(os.path.dirname(b), exist_ok=True); tmp = b + ".tmp"; shutil.copy2(p, tmp); os.replace(tmp, b); n += 1
    yedekteki = {rel: sha1(os.path.join(hedef, rel)) for rel in liste if os.path.isfile(os.path.join(hedef, rel))}
    fark = liste_fark(liste, yedekteki)
    ortak.atomik_yaz(os.path.join(hedef, LISTE_ADI), {
        "_surum": 1, "_uretim": {"arac_surum": SURUM, "zaman": simdi(), "ortam": ortam(), "sonuc": "HATA" if fark else "GEC"},
        "kaynak": kaynak, "dosya_sayisi": len(liste), "dosyalar": liste})
    return {"durum": "hata" if fark else "tamam", "hedef": hedef, "kopyalanan": n, "dogrulanan": len(yedekteki), "fark": fark}


def dogrula(kaynak, hedef, ekler=None, kok=None):
    """Yedeğin SHA1_LISTESI'ni şimdiki kaynakla karşılaştırır (dosya okumaz yedekten; liste yoksa 'yedek yok')."""
    yl = ortak.json_oku(os.path.join(hedef, LISTE_ADI))
    if not surucu_var(kok or hedef): return {"durum": "ertelendi", "neden": "yedek sürücüsü takılı değil", "fark": []}
    if not isinstance(yl, dict): return {"durum": "yedek_yok", "fark": [{"dosya": "*", "neden": "yedek hiç alınmamış"}]}
    simdi_l = sha1_listesi(kaynak)
    for rel, p in (ekler or {}).items():
        if p and os.path.isfile(p): simdi_l[rel] = sha1(p)
    fark = liste_fark(simdi_l, yl.get("dosyalar") or {})
    return {"durum": "fark" if fark else "ayni", "fark": fark, "yedek_zamani": (yl.get("_uretim") or {}).get("zaman")}


def durum_yaz(anahtar, sonuc):
    """<veri>/HESAP/YEDEK_DURUMU.json: {anahtar: {durum, zaman, hedef, fark_sayisi}} (A00 bilgi için)."""
    try: p = os.path.join(ortak.yollar()["hesap"], "YEDEK_DURUMU.json")
    except ortak.YolYok: return None
    d = ortak.json_oku(p, {}) or {}
    d[anahtar] = {"durum": sonuc.get("durum"), "zaman": simdi(), "hedef": sonuc.get("hedef"), "fark_sayisi": len(sonuc.get("fark") or []),
                  "neden": sonuc.get("neden")}
    d["_surum"] = 1
    ortak.atomik_yaz(p, d)
    return p


# --- ders defteri ------------------------------------------------------------------------------------------------
def ders_kaynaklari():
    b = os.path.join(ortak.yollar()["veri_kok"], "BILGI")
    return os.path.join(b, "DERSLER"), {"_BILGI/KURALLAR_OGRENILEN.json": os.path.join(b, "KURALLAR_OGRENILEN.json"),
                                       "_BILGI/DERSLER_AKTIF.md": os.path.join(b, "DERSLER_AKTIF.md")}


def yedek_koku(hedef_kok=None): return os.path.abspath(hedef_kok or ortak.yollar()["yedek"])


def ders_hedefi(hedef_kok=None): return os.path.join(yedek_koku(hedef_kok), "DERSLER")


def ders_yedekle(hedef_kok=None):
    kaynak, ekler = ders_kaynaklari()
    os.makedirs(kaynak, exist_ok=True)
    r = kopya_yedek(kaynak, ders_hedefi(hedef_kok), ekler, kok=yedek_koku(hedef_kok))
    durum_yaz("dersler", r)
    return r


def ders_dogrula(hedef_kok=None):
    kaynak, ekler = ders_kaynaklari()
    return dogrula(kaynak, ders_hedefi(hedef_kok), ekler, kok=yedek_koku(hedef_kok))


def mesaj(ad, r):
    if r["durum"] == "ertelendi":
        return f"{ad} yedeği ertelendi: {r.get('neden')}. D diski takılınca sonraki filmin başında yeniden denenir (bilgi)."
    if r["durum"] == "hata":
        return f"!! {ad} yedeğinde HATA: {r.get('neden') or ''} " + "; ".join(f"{x['dosya']} ({x['neden']})" for x in r["fark"][:10])
    if "kopyalanan" in r:
        return f"{ad} yedeği tamam: {r['dogrulanan']} dosya sha1 ile doğrulandı ({r['kopyalanan']} kopyalandı) → {r['hedef']}"
    return f"{ad} yedek karşılaştırması: {r['durum']} ({len(r['fark'])} fark)"


def main(argv):
    hedef = argv[argv.index("--hedef") + 1] if "--hedef" in argv and argv.index("--hedef") + 1 < len(argv) else None
    bilinen = {"--hedef", "--dogrula", "--yenile", "--yedekle", "--film"}
    if any(a.startswith("--") and a not in bilinen for a in argv) or "-h" in argv: print(__doc__); return ORTAM
    try:
        if "--dogrula" in argv:
            r = ders_dogrula(hedef); print(mesaj("Ders defteri", r))
            if r["durum"] in ("fark", "yedek_yok") and "--yenile" in argv:
                r = ders_yedekle(hedef); print(mesaj("Ders defteri", r)); return HATA if r["durum"] == "hata" else BITTI
            return BITTI
        r = ders_yedekle(hedef); print(mesaj("Ders defteri", r))
        return HATA if r["durum"] == "hata" else BITTI
    except ortak.YolYok as e:
        print("!!", e); return ORTAM


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
