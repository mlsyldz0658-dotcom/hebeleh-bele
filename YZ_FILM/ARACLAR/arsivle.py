"""ARŞİVLE — disk kapısı ve kendiliğinden arşiv: yeniden üretilebilir ara dosyaları D'ye TAŞIR (TASARIM D-38, §6.1; [SON] O-7).

Kullanım:
  python arsivle.py --film <film> [--kuru] [--disk]
    --kuru: yalnız listeler (hiçbir şey taşınmaz) · --disk: yalnız boş yer disk_bos_min_gb (20 GB, tahmin) altındaysa çalışır
  A16 ve A17 sonunda ve disk kapısında Claude kendisi başlatır; ARSIVLE.bat yalnız kullanıcı isterse elle çalıştırma içindir.
Taşınanlar (<arsiv>/<film>/<aynı göreli yol>; <arsiv> = YOLLAR.json "arsiv", Windows'ta D:\\YZ_FILM_ARSIV):
  render önbelleği (KURGU/_onbellek), eski 1080p türevleri (KURGU/klipler_1080), büyütme pencereleri, eski taslak inceleme kopyaları,
  KURGU/surumler/'in SON İKİ sürümü dışındakiler, eski animatik ve kesit render'ları (en yenisi kalır), videosu GEÇ olan planların seçilmeyen
  görsel adayları (SIRALI_GORSEL/_ADAYLAR), eski çekimler (SIRALI_VIDEO/_ESKI) ve film _ESKI/.
Taşınmayanlar (testli): son taslağın bağlı olduğu yollar (draft_content.json path'leri), açık kuyruk maddelerinin (bekliyor/gönderildi)
girdileri, dışa aktarılmamış iş (yayın dosyası yoksa son kurgu sürümü ve stemler). Atlananlar da listelenir.
Yöntem: Windows'ta robocopy /MOV (dosya) ya da /E /MOVE (klasör); ayna bayrağı ASLA kullanılmaz (kaynakta olmayanı hedefte silerdi).
Başka sistemde shutil.move. Kalıcı silme yok. Arşivde AYNI ADLI dosya varsa üzerine yazılmaz: önceden denetlenir, kaynak yerinde kalır
(rapor: atlanan_arsivde_var); robocopy'ye de /XC /XN /XO verilir (değişmiş/yeni/eski hiçbir hedef dosyanın üzerine yazılmaz). Taşınanların listesi kullanıcıya BİLGİ olarak verilir (_RAPOR/ARSIV_<zaman>.json).
D takılı değilse 8 BEKLE + tek fiziksel iş "D'yi tak" (film.py bekle --kullanici diski yoklar).
Çıkış kodları: 0 tamam · 1 taşıma hatası · 2 film yok · 8 BEKLE (arşiv diski takılı değil).
"""
import os, sys, re, glob, time, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kurgu_ortak as ko

SURUM = "arsivle 1.0"
YASAK_BAYRAK = "/" + "MIR"           # kaynakta yazılı tutulmaz; komut kurucu bunu asla üretmez (testli)
D_TAK = "Arşiv diski (D:) takılı değil. D'yi tak; takınca ben kendim devam ederim."


def arsiv_koku():
    y = ortak.yollar(); return y.get("arsiv") or os.path.join(y["veri_kok"], "_ARSIV")


def disk_takili(kok_):
    if os.name == "nt":
        surucu = os.path.splitdrive(os.path.abspath(kok_))[0]
        return bool(surucu) and os.path.exists(surucu + "\\")
    return os.path.isdir(os.path.dirname(os.path.abspath(kok_.rstrip(os.sep))))


def _tum(kok, rel):
    p = os.path.join(kok, rel)
    if os.path.isfile(p): return [p]
    return [os.path.join(a, d) for a, _, ds in os.walk(p) for d in ds] if os.path.isdir(p) else []


def adaylar(kok):
    c = []
    for rel in ("KURGU/_onbellek", "KURGU/klipler_1080", "_ESKI", "SIRALI_VIDEO/_ESKI"): c += _tum(kok, rel)
    c += glob.glob(os.path.join(kok, "KURGU", "surumler", "v*", "buyuk", "_pencere", "*"))
    kopyalar = sorted(glob.glob(os.path.join(kok, "KURGU", "_TASLAK_KOPYA", "*")))
    for k in kopyalar[:-1]: c += _tum(kok, os.path.relpath(k, kok))
    surumler = sorted([d for d in glob.glob(os.path.join(kok, "KURGU", "surumler", "v*")) if os.path.isdir(d) and d.rsplit("v", 1)[-1].isdigit()],
                      key=lambda d: int(d.rsplit("v", 1)[-1]))
    for d in surumler[:-2]: c += _tum(kok, os.path.relpath(d, kok))
    for klasor, desen in (("ANIMATIK", "*.mp4"), ("KESIT", "*.mp4")):
        fs = sorted(glob.glob(os.path.join(kok, klasor, desen)), key=os.path.getmtime)
        c += fs[:-1]
    gec = {p.get("no") for p in ko.sahne_planlari(kok).values() if ((p.get("denetim") or {}).get("V2") or {}).get("sonuc") == "GEC"}
    for f in glob.glob(os.path.join(kok, "SIRALI_GORSEL", "_ADAYLAR", "*")):
        m = re.match(r"(\d+)", os.path.basename(f))
        if m and int(m.group(1)) in gec and os.path.isfile(f): c.append(f)
    return sorted({os.path.abspath(x) for x in c if os.path.isfile(x)})


def bagli_yollar(kok):
    """Son taslağın (ve yayın taslağının) bağlı olduğu dosyalar + KURGU_PLANI'nın ve ses çizelgesinin kullandıkları."""
    import capcut_taslak as ct
    out = set()
    for ad in ("son_capcut_projesi.json", "son_capcut_projesi_yayin.json"):
        pj = ortak.json_oku(os.path.join(kok, "KURGU", ad), {}) or {}
        if pj.get("klasor"):
            o = ct.oku(pj["klasor"])
            for s in ct.segmentler(o["icerik"]) if o.get("icerik") else []:
                if s.get("yol"): out.add(os.path.abspath(s["yol"]))
        for s in pj.get("segmentler") or []:
            if s.get("kaynak"): out.add(os.path.abspath(ko.mutlak(kok, s["kaynak"])))
    _, kp = ko.kurgu_plani(kok)
    for x in (kp or {}).get("planlar") or []:
        if x["goruntu"].get("dosya"): out.add(os.path.abspath(ko.mutlak(kok, x["goruntu"]["dosya"])))
    sc = ko.ses_cizelgesi(kok)
    for k in ("ambiyans", "efektler", "muzik"):
        for e in sc.get(k) or []:
            if e.get("dosya"): out.add(os.path.abspath(ko.mutlak(kok, e["dosya"])))
    return out


def kuyruk_girdileri(kok):
    """Açık kuyruk maddelerinin (bekliyor, gönderildi) planları ve girdi yolları."""
    planlar, yollar = set(), set()
    for ad in ("YENIDEN_URET", "YENIDEN_YAZ"):
        q = ortak.json_oku(os.path.join(kok, "KUYRUK", ad + ".json"), {}) or {}
        for m in q.get("maddeler") or []:
            if m.get("durum") not in ("bekliyor", "gonderildi"): continue
            if isinstance(m.get("plan"), int): planlar.add(m["plan"]); planlar.update(m.get("zincir_etkisi") or [])
            for g in m.get("girdi") or []: yollar.add(os.path.abspath(ko.mutlak(kok, g)))
    return planlar, yollar


def disa_aktarildi(kok): return bool(glob.glob(os.path.join(kok, "YAYIN", "*_4K.mp4")) or glob.glob(os.path.join(kok, "YAYIN", "*_master.mp4")))


def robocopy_komutu(kaynak_dir, hedef_dir, dosyalar=None):
    """Taşıma komutu: dosya listesi → /MOV; klasör → /E /MOVE. Ayna bayrağı hiçbir koşulda eklenmez."""
    k = ["robocopy", kaynak_dir, hedef_dir] + (list(dosyalar) if dosyalar else []) + (["/MOV"] if dosyalar else ["/E", "/MOVE"]) + \
        ["/XC", "/XN", "/XO", "/R:1", "/W:1", "/NP", "/NFL", "/NDL"]          # hedefte aynı adlı dosya varsa üzerine yazma
    assert YASAK_BAYRAK not in [x.upper() for x in k]
    return k


def tasi(kok, dosyalar, hedef_kok, arsivde_var=None):
    """Dosyaları arşive taşır; arşivde aynı adlı dosya varsa ONA DOKUNMAZ (kaynak yerinde kalır, arsivde_var listesine yazılır).
    Taşındı sayılan her dosya: kaynakta yok VE hedefte var (doğrulanır)."""
    arsivde_var = [] if arsivde_var is None else arsivde_var
    gruplar = {}
    for p in dosyalar: gruplar.setdefault(os.path.dirname(p), []).append(os.path.basename(p))
    tasinan = []
    for d, adlar in sorted(gruplar.items()):
        hedef = os.path.join(hedef_kok, os.path.relpath(d, kok)); os.makedirs(hedef, exist_ok=True)
        bos = []
        for a in adlar:
            if os.path.lexists(os.path.join(hedef, a)): arsivde_var.append(ko.goreli(kok, os.path.join(d, a)))
            else: bos.append(a)
        if os.name == "nt":
            for i in range(0, len(bos), 50):
                r = subprocess.run(robocopy_komutu(d, hedef, bos[i:i + 50]), capture_output=True, text=True)
                if r.returncode >= 8: raise RuntimeError(f"robocopy {r.returncode}: {d}")
        else:
            for a in bos:
                h = os.path.join(hedef, a)
                if os.path.lexists(h): continue                      # arada belirdiyse dokunulmaz (aşağıda arsivde_var)
                shutil.move(os.path.join(d, a), h)
        for a in bos:
            g = ko.goreli(kok, os.path.join(d, a))
            if not os.path.exists(os.path.join(d, a)) and os.path.exists(os.path.join(hedef, a)): tasinan.append(g)
            elif g not in arsivde_var: arsivde_var.append(g)
    return tasinan


def arsivle(kok, argv=()):
    argv = list(argv); kuru = ko.bayrak(argv, "--kuru")
    if ko.bayrak(argv, "--disk"):
        bos = shutil.disk_usage(kok).free / 1e9; esik = float(ko.esik("disk_bos_min_gb", 20) or 20)
        if bos >= esik: print(f"disk boş yeri {bos:.1f} GB ≥ {esik:.0f} GB: arşiv gerekmiyor", flush=True); return 0, None
    hedef_kok = os.path.join(arsiv_koku(), os.path.basename(os.path.normpath(kok)))
    if not kuru and not disk_takili(arsiv_koku()):
        print(D_TAK, flush=True); return ko.BEKLE, {"kullaniciya": D_TAK}
    aday = adaylar(kok); bagli = bagli_yollar(kok); kplan, kyol = kuyruk_girdileri(kok); disa = disa_aktarildi(kok)
    _, kp = ko.kurgu_plani(kok); son_v = os.path.join(kok, "KURGU", "surumler", f"v{(kp or {}).get('kurgu_surumu', 0)}")
    tasinacak, atl_b, atl_k, atl_d = [], [], [], []
    for p in aday:
        if p in bagli: atl_b.append(ko.goreli(kok, p)); continue
        m = re.match(r"(\d{3})", os.path.basename(p))
        if p in kyol or (m and int(m.group(1)) in kplan and any(k in p for k in ("SIRALI_VIDEO", "SIRALI_GORSEL", "KUNYE"))):
            atl_k.append(ko.goreli(kok, p)); continue
        if not disa and os.path.abspath(p).startswith(os.path.abspath(son_v) + os.sep): atl_d.append(ko.goreli(kok, p)); continue
        tasinacak.append(p)
    boyut = sum(os.path.getsize(p) for p in tasinacak) / 1e6
    arsivde_var = []
    tasinan = [] if kuru else tasi(kok, tasinacak, hedef_kok, arsivde_var)
    rap = {"_uretim": ko.po.zarf("A16", SURUM), "hedef": hedef_kok, "kuru": kuru, "yontem": "robocopy /MOV · /E /MOVE" if os.name == "nt" else "shutil.move",
           "tasinan": tasinan if not kuru else [ko.goreli(kok, p) for p in tasinacak], "boyut_mb": round(boyut, 1),
           "atlanan_bagli": atl_b, "atlanan_kuyruk": atl_k, "atlanan_disa_aktarilmamis": atl_d, "atlanan_arsivde_var": arsivde_var}
    ortak.atomik_yaz(os.path.join(kok, "_RAPOR", f"ARSIV_{time.strftime('%Y%m%d-%H%M%S')}.json"), rap)
    ne = "taşınacak" if kuru else "D'ye taşındı"
    print(f"Bilgi: {ne}: {len(rap['tasinan'])} dosya ({boyut:.0f} MB) → {hedef_kok}. "
          f"Atlanan: taslağa bağlı {len(atl_b)}, açık kuyruk {len(atl_k)}, dışa aktarılmamış {len(atl_d)}.", flush=True)
    return 0, rap


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    try: k, _ = arsivle(kok, argv)
    except RuntimeError as e: print(f"!! {e}", flush=True); return 1
    return k


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
