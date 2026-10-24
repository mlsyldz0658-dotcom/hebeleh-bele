"""KOŞ — bütün test takımını modül (uzun modüllerde sınıf grubu) başına ayrı süreçte, paralel koşturur
(TASARIM §6.10: bütün takım ≤ 10 dk; §9 adım 18 CI).

Kullanım (YZ_FILM klasöründen ya da herhangi bir yerden):
  python ARACLAR/testler/kos.py                    bütün test_*.py, işlemci sayısı kadar paralel
  python ARACLAR/testler/kos.py -j 2               2 süreç
  python ARACLAR/testler/kos.py test_kurgu test_ses   yalnız bu modüller (BOL'dakiler gruplara bölünür)
  python ARACLAR/testler/kos.py --sure             birim sürelerini uzundan kısaya yazar
Sıradan yol da geçerlidir: python -m unittest discover -s ARACLAR/testler (tek süreç; aynı testler).

Neden güvenli: her süreç `_ortam` ile kendi geçici veri kökünü ve YOLLAR.json'unu kurar (YZ_FILM_YOLLAR); süreçler arası paylaşılan
tek şey YZ_TEST_ONBELLEK'teki salt okunur fikstür önbelleğidir (ör. test_yayin medyası: bir süreç kurar, öbürleri bekleyip kopyalar).
Bölünen modülde her test tam bir kez koşar (test_kullanici_yuzu.Kosucu bunu yükleyiciyle denetler). Uzun birimler önce başlar.
Çıkış: 0 hepsi geçti · 1 en az bir birim kaldı (onun çıktısı yazılır).
"""
import os, sys, ast, time, shutil, tempfile, subprocess
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
# Yaklaşık süre (sn; tek çekirdek, 24.10.2026 ölçümü). Yalnız başlatma sırası içindir; yanlışsa sonuç değişmez.
SURE_IPUCU = {"test_yayin": 50, "test_yayin.KaliteFinal": 75, "test_kurgu": 60, "test_gorev_defteri": 25, "test_kancalar": 25,
              "test_kancalar.TestErisim+TestKomut+TestGuvenlikInceleme": 25, "test_ses_hazirlik": 50, "test_ses_tam": 40,
              "test_uctan_uca_tam_sahte": 18, "test_v1": 17, "test_yollar": 16,
              "test_memmet_korkuluk": 10, "test_memmet_korkuluk.Yama": 80, "test_memmet_korkuluk.HerAn": 70,
              "test_kurgu.T18_CilaBuyutKur3+T19_Birlestirme": 45, "test_gorev_defteri.KesmeSenaryolari": 30}
# Uzun modüllerde ağır sınıflar ayrı süreçte koşar (her sınıf bağımsızdır: kendi setUp'ı ve _ortam'ı); modülün kalan sınıfları bir
# süreçte birlikte koşar (süreç içi fikstür önbelleği korunur). Sonuç aynıdır, yalnız duvar saati kısalır: ör. memmet_korkuluk'ta
# yama testinin yamalı kopyadaki T10 koşusu HerAn taramasıyla aynı anda koşar.
BOL = {"test_memmet_korkuluk": (("Yama",), ("HerAn",)),
       "test_yayin": (("KaliteFinal",),),                # medya fikstürü YZ_TEST_ONBELLEK'te bir kez kurulur (test_yayin.medya_kur)
       "test_kancalar": (("TestErisim", "TestKomut", "TestGuvenlikInceleme"),),
       "test_kurgu": (("T18_CilaBuyutKur3", "T19_Birlestirme"),),
       "test_gorev_defteri": (("KesmeSenaryolari",),)}


def siniflar(m):
    """Modüldeki test sınıfları (ast; modül içe aktarılmaz): kendisinde ya da modül içindeki atasında test_ yöntemi olan sınıflar."""
    with open(os.path.join(HERE, m + ".py"), encoding="utf-8") as f: agac = ast.parse(f.read())
    sin = {n.name: n for n in agac.body if isinstance(n, ast.ClassDef)}

    def testli(ad, gorulen=()):
        n = sin.get(ad)
        if n is None or ad in gorulen: return False
        if any(isinstance(x, ast.FunctionDef) and x.name.startswith("test") for x in n.body): return True
        return any(testli(getattr(b, "id", None), gorulen + (ad,)) for b in n.bases)
    return [ad for ad in sin if testli(ad)]


def isler(secili=None):
    """Koşu birimleri [(ad, [unittest hedefleri])]: modül ya da BOL'daki gruplar + modülün kalanı. Uzun olan önce."""
    hepsi = sorted(f[:-3] for f in os.listdir(HERE) if f.startswith("test_") and f.endswith(".py"))
    if secili: hepsi = [m for m in hepsi if m in {s[:-3] if s.endswith(".py") else s for s in secili}]
    out = []
    for m in hepsi:
        if m not in BOL: out.append((m, [m])); continue
        s = siniflar(m); kalan = list(s)
        for g in BOL[m]:
            g = [c for c in g if c in kalan]
            if not g: continue
            out.append((f"{m}." + "+".join(g), [f"{m}.{c}" for c in g])); kalan = [c for c in kalan if c not in g]
        if kalan: out.append((m, [f"{m}.{c}" for c in kalan]))
    ipucu = lambda ad: SURE_IPUCU.get(ad) or os.path.getsize(os.path.join(HERE, ad.split(".")[0] + ".py")) / 2000.0
    return sorted(out, key=lambda x: -ipucu(x[0]))


def kos1(is_):
    ad, hedef = is_; t = time.time()
    r = subprocess.run([sys.executable, "-m", "unittest"] + hedef, cwd=HERE, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"))
    son = [s for s in (r.stderr or "").strip().splitlines() if s.strip()]
    return ad, r.returncode, time.time() - t, r.stdout + r.stderr, (son[-1] if son else "")


def main(a=None):
    a = sys.argv[1:] if a is None else list(a)
    j = os.cpu_count() or 2
    if "-j" in a: i = a.index("-j"); j = int(a[i + 1]); del a[i:i + 2]
    sure = "--sure" in a; a = [x for x in a if x != "--sure"]
    ms = isler(a or None); t0 = time.time(); sonuc = []
    kendi = not os.environ.get("YZ_TEST_ONBELLEK")
    if kendi: os.environ["YZ_TEST_ONBELLEK"] = tempfile.mkdtemp(prefix="yz_test_onbellek_")
    print(f"{len(ms)} koşu birimi (modül ya da sınıf grubu), {j} paralel süreç", flush=True)
    try:
        with ThreadPoolExecutor(max_workers=max(1, j)) as ex:
            for m, kod, sn, cikti, son in ex.map(kos1, ms):
                sonuc.append((m, kod, sn, cikti)); print(f"  {'GEÇTİ' if kod == 0 else 'KALDI'} {m} ({sn:.1f} sn) {son}", flush=True)
    finally:
        if kendi: shutil.rmtree(os.environ.pop("YZ_TEST_ONBELLEK"), ignore_errors=True)   # yalnız bu koşunun geçici önbelleği (_ortam gibi)
    kalan = [x for x in sonuc if x[1] != 0]
    for m, _, _, cikti in kalan: print(f"\n===== {m} =====\n{cikti[-20000:]}")
    if sure:
        print("\nSüreler:"); [print(f"  {sn:7.1f}  {m}") for m, _, sn, _ in sorted(sonuc, key=lambda x: -x[2])]
    print(f"\nToplam {time.time() - t0:.1f} sn · {len(ms) - len(kalan)}/{len(ms)} birim geçti")
    return 1 if kalan else 0


if __name__ == "__main__":
    sys.exit(main())
