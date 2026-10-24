"""KASET sağlayıcısı — kaydedilmiş ajan (ve gerektiğinde betik) çıktılarını ağsız, kredisiz yeniden oynatır (TASARIM §6.10, D-41).
Yalnız test kipindedir (veri/ADLAR.json saglayici_yalniz_test); üretimde kullanılmaz. Kaset bir şey uydurmaz: kayıt yoksa KasetYok.

Kaset klasörü: <film>/_KASET/ (ya da YZ_FILM_KASET ortam değişkeni). Düzen:
  AJAN/<aşama>_<görev kodu>/<anahtar>/<CIKTI'deki göreli yol>      ör. AJAN/A03_HM/D/oneri.md, AJAN/A06_HS/t2_A/rapor.json
  BETIK/<aşama>_<görev kodu>/<anahtar>/<film köküne göreli yol>    ör. BETIK/A06_KP/hepsi/_KOR_PAKET/kagit_t{tur}/A/P0/PAKET.md
  Anahtar arama sırası: t<tur>_<persona> · t<tur>_<kip> · t<tur>_<i> · t<tur> · <persona> · <kip> · <i> · hepsi
  (i = görevin örnek numarası, anahtar "A06@s1/t1/g2/HS/<i>"'den). Yol adlarında {tur} görevin tur numarasıyla değişir.
  BETIK kaydındaki JSON kapı raporlarının (_uretim olan) _uretim.gorev / tur / zaman alanları oynatırken görevin değerleriyle yazılır;
  _cikis dosyası (içinde sayı) varsa çıkış kodudur (varsayılan 0).
Kullanım:
  python saglayicilar/kaset.py oynat --gorev <id> --film <film>     ajan görevinin CIKTI/'sını kasetten yazar (sonra film.py bitir)
  python saglayicilar/kaset.py betik --gorev <id> --film <film>     betik görevinin çıktılarını kasetten yazar
  python saglayicilar/kaset.py kaydet --gorev <id> --film <film> [--anahtar t1]   biten ajan görevinin CIKTI'sını kasete kaydeder
  Kodda: from saglayicilar.kaset import Kaset, ajan_oynat, betik_oynat, kaydet, KasetYok
Çıkış kodları: 0 tamam · 1 kayıt yok (KasetYok) ya da kullanım · 4 YOLLAR.json yok.
"""
import os, re, sys, json, shutil, datetime
ARACLAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
import ortak
from saglayicilar import Saglayici


class KasetYok(Exception):
    """Bu görev için kaset kaydı yok (kaset uydurmaz)."""


def kaset_kok(film):
    return os.environ.get("YZ_FILM_KASET") or os.path.join(film, "_KASET")


def _i(g):
    try: return int(str(g.get("anahtar", "")).rsplit("/", 1)[-1])
    except ValueError: return 1


def gorev_kodu(g): return f"{g['asama']}_{g['id'].split('-')[1]}"


def anahtarlar(g):
    t = f"t{g.get('tur_no') or 1}"; out = []
    for x in (g.get("persona"), g.get("kip"), str(_i(g))):
        if x: out.append(f"{t}_{x}")
    out.append(t)
    for x in (g.get("persona"), g.get("kip"), str(_i(g))):
        if x: out.append(str(x))
    out.append("hepsi")
    return out


def bul(film, g, tur="AJAN"):
    kok = os.path.join(kaset_kok(film), tur, gorev_kodu(g))
    for a in anahtarlar(g):
        p = os.path.join(kok, a)
        if os.path.isdir(p): return p
    raise KasetYok(f"kaset kaydı yok: {tur}/{gorev_kodu(g)}/{{{', '.join(anahtarlar(g))}}}")


def _dosyalar(kl):
    for k, ds, fs in os.walk(kl):
        ds.sort()
        for f in sorted(fs):
            if f == "_cikis": continue
            p = os.path.join(k, f); yield p, os.path.relpath(p, kl)


def _yaz(src, hedef, g=None, zarf=False):
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    if zarf and src.endswith(".json"):
        j = ortak.json_oku(src)
        if isinstance(j, dict) and isinstance(j.get("_uretim"), dict):
            j["_uretim"].update(gorev=g["id"], zaman=datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
            if "tur" in j and isinstance(j["tur"], int): j["tur"] = g.get("tur_no") or 1
            ortak.atomik_yaz(hedef, j); return
    tmp = hedef + ".tmp"; shutil.copyfile(src, tmp); os.replace(tmp, hedef)


def _rel(rel, g): return rel.replace("{tur}", str(g.get("tur_no") or 1)).replace("{i}", str(_i(g)))


def ajan_oynat(film, g, gdir=None):
    """CIKTI/ dosyalarını yazar; yazılan göreli yolları döndürür."""
    gdir = gdir or os.path.join(film, "_GOREV", g["id"]); kl = bul(film, g, "AJAN"); out = []
    for p, rel in _dosyalar(kl):
        r = "CIKTI/" + _rel(rel, g).replace(os.sep, "/")
        _yaz(p, os.path.join(gdir, r)); out.append(r)
    return out


def betik_oynat(film, g):
    """(çıkış kodu, yazılan dosyalar)."""
    kl = bul(film, g, "BETIK"); out = []
    for p, rel in _dosyalar(kl):
        r = _rel(rel, g)
        _yaz(p, os.path.join(film, r), g, zarf=True); out.append(r)
    kod = 0
    cp = os.path.join(kl, "_cikis")
    if os.path.isfile(cp):
        try:
            with open(cp, encoding="utf-8") as f: kod = int(f.read().strip() or 0)
        except ValueError: kod = 1
    return kod, out


def kaydet(film, g, anahtar=None):
    """Biten ajan görevinin CIKTI'sını AJAN/<kod>/<anahtar>/ altına kopyalar (var olan kayıt _ESKI'ye taşınır; silinmez)."""
    gdir = os.path.join(film, "_GOREV", g["id"], "CIKTI")
    hedef = os.path.join(kaset_kok(film), "AJAN", gorev_kodu(g), anahtar or f"t{g.get('tur_no') or 1}_{g.get('persona') or _i(g)}")
    if os.path.isdir(hedef):
        eski = os.path.join(kaset_kok(film), "_ESKI", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), os.path.relpath(hedef, kaset_kok(film)))
        os.makedirs(os.path.dirname(eski), exist_ok=True); shutil.move(hedef, eski)
    shutil.copytree(gdir, hedef)
    return hedef


class Kaset(Saglayici):
    """llm türü için kayıttan oynatıcı (claude_code / claude_api yerine testte)."""
    ad = "kaset"
    turler = ("llm",)
    kredili = False

    def __init__(self, film=None): self.film = film

    def hazir(self):
        if self.film and not os.path.isdir(kaset_kok(self.film)): return False, "kaset klasörü yok"
        return True, ""

    def ajan(self, film, g, gdir=None): return ajan_oynat(film, g, gdir)

    def betik(self, film, g): return betik_oynat(film, g)


def main(a):
    def arg(ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v
    if not a or a[0] not in ("oynat", "betik", "kaydet"): print(__doc__); return 1
    film, gid = arg("--film"), arg("--gorev")
    if not (film and gid): print("!! --film ve --gorev gerekli"); return 1
    try:
        if not os.path.isdir(film): film = os.path.join(ortak.yollar()["filmler"], film)
    except ortak.YolYok as e: print("!!", e); return 4
    g = ortak.json_oku(os.path.join(film, "_GOREV", gid, "GOREV.json"))
    if not isinstance(g, dict): print(f"!! görev yok: {gid}"); return 1
    try:
        if a[0] == "oynat": print("\n".join(ajan_oynat(film, g))); return 0
        if a[0] == "betik": kod, out = betik_oynat(film, g); print("\n".join(out)); return kod
        print(kaydet(film, g, arg("--anahtar"))); return 0
    except KasetYok as e:
        print("!!", e); return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
