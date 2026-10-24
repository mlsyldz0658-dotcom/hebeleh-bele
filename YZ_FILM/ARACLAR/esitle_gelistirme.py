"""GELİŞTİRME EŞİTLEME (dar hâl, D-12) — yerel geliştirme oturumunun <veri>/GELISTIRME/ klasöründe hazırladığı
dosyaları depoya, AYRI BİR DALDA commit'leyip iter. Birleştirme bulutta PR ile olur; bu araç ana dala ya da
o an açık dala asla yazmaz.

  python esitle_gelistirme.py [--veri <klasör>] [--depo <klasör>] [--ad memmet3] [--kuru] [--push-yok]

  --veri      veri kökü (varsayılan: Masaüstü\\YZ_FILM). Kaynak: <veri>\\GELISTIRME\\
  --depo      git deposu (varsayılan: bu dosyanın bulunduğu depo)
  --ad        dal adının parçası: yerel/<ad>-<tarih>  (varsayılan: gelistirme)
  --kuru      hiçbir şeyi değiştirmez; yalnız ne yapılacağını ve tarama sonucunu yazar
  --push-yok  commit'ler ama itmez (dal yerelde kalır)

Ne kopyalanır (beyaz liste): GELISTIRME altındaki .py .md .json .bat .txt dosyaları, 1 MB'tan küçükse.
Asla kopyalanmaz: AYARLAR, memmet_profil, __pycache__, .git, _ESKI klasörleri; adında anahtar/token/secret geçen
dosyalar; video/görsel/ses ve beyaz listede olmayan her şey; kısayol (symlink) dosyaları.
Nereye gider: GELISTIRME\\kalibrasyon\\... → YZ_FILM/ARACLAR/veri/kalibrasyon/...; geri kalan her şey
YZ_FILM/GELISTIRME/... altına (yerleştirme bulut oturumunda PR içinde yapılır).

Kopyalamadan ÖNCE anahtar taraması yapılır: bilinen anahtar kalıpları + <veri>\\AYARLAR ve depodaki
YZ_FILM\\AYARLAR içindeki .txt anahtar dosyalarının içeriği (yalnız bellekte; ekrana ASLA yazılmaz, yalnız
dosya adı ve satır numarası yazılır). Tek bir bulgu olursa hiçbir şey kopyalanmaz, hiçbir şey commit'lenmez.

Çıkış kodları: 0 tamam · 3 anahtar bulundu · 4 ortam (depo kirli, git deposu değil, GELISTIRME yok) · 1 hata
(push başarısız olursa da 1: commit yerel dalda durur, dosyalar GELISTIRME'de kalır).
"""
import os, re, sys, shutil, argparse, subprocess, datetime
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))

IZINLI_UZANTI = {".py", ".md", ".json", ".bat", ".txt"}
YASAK_KLASOR = {"ayarlar", "memmet_profil", "__pycache__", ".git", "_eski", "node_modules"}
YASAK_AD = re.compile(r"anahtar|token|secret|credential|\.env", re.I)
AZAMI_BOYUT = 1024 * 1024
KORUNAN_DAL = {"main", "master"}
# GELISTIRME içindeki önek → depodaki hedef (ilk eşleşen kazanır; "" geri kalan her şey)
ESLEME = [("kalibrasyon/", "YZ_FILM/ARACLAR/veri/kalibrasyon/"), ("", "YZ_FILM/GELISTIRME/")]

KALIPLAR = [
    ("telegram_bot_token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}")),
    ("openai_benzeri_key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}")),
    ("elevenlabs_benzeri_key", re.compile(r"\bsk_[0-9a-f]{40,}\b")),
    ("ozel_anahtar", re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
]
# api_key = "...", "xi-api-key": "...", set AI84_API_KEY=... (değer sonra ayrıca süzülür)
GENEL = re.compile(r"(?:api|xi)[_-]?(?:api[_-]?)?key[\"']?\s*[:=]\s*(\S{16,})", re.I)
HEX32 = re.compile(r"(?<![0-9A-Fa-f])[0-9a-f]{32}(?![0-9A-Fa-f])")  # AI84/ElevenLabs eski biçim
HEX32_BAGLAM = re.compile(r"key|anahtar|token|xi-api", re.I)


class OrtamHatasi(Exception): pass


def varsayilan_veri(): return os.path.join(os.path.expanduser("~"), "Desktop", "YZ_FILM")


def git(depo, *args, kontrol=True):
    r = subprocess.run(["git", "-C", depo, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if kontrol and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:2])} başarısız: {r.stderr.strip()[:300]}")
    return r


# ---------- seçim ----------

def sec(gelistirme):
    """(alinanlar: [göreli yol], atlananlar: [(göreli yol, neden)])"""
    alinan, atlanan = [], []
    for kok, klasorler, dosyalar in os.walk(gelistirme):
        rel_kok = os.path.relpath(kok, gelistirme)
        for k in list(klasorler):
            if k.lower() in YASAK_KLASOR or os.path.islink(os.path.join(kok, k)):
                klasorler.remove(k)
                atlanan.append((os.path.normpath(os.path.join(rel_kok, k)).replace(os.sep, "/") + "/", "yasak klasör"))
        klasorler.sort()
        for d in sorted(dosyalar):
            yol = os.path.join(kok, d)
            rel = os.path.normpath(os.path.join(rel_kok, d)).replace(os.sep, "/")
            if os.path.islink(yol): atlanan.append((rel, "kısayol")); continue
            if os.path.splitext(d)[1].lower() not in IZINLI_UZANTI: atlanan.append((rel, "beyaz listede değil")); continue
            if YASAK_AD.search(d): atlanan.append((rel, "adı anahtar dosyasına benziyor")); continue
            if os.path.getsize(yol) > AZAMI_BOYUT: atlanan.append((rel, "1 MB'tan büyük")); continue
            alinan.append(rel)
    return alinan, atlanan


def hedef(rel):
    for onek, h in ESLEME:
        if rel.startswith(onek): return h + rel[len(onek):]
    raise ValueError(rel)


# ---------- anahtar taraması ----------

def bilinen_anahtarlar(klasorler):
    """AYARLAR/*.txt içindeki anahtar benzeri satırlar (yalnız bellekte; asla yazdırılmaz)."""
    gizli = set()
    for k in klasorler:
        if not os.path.isdir(k): continue
        for ad in os.listdir(k):
            if not ad.lower().endswith(".txt") or ad.upper().startswith(("OKU_BENI", "README")): continue
            try:
                with open(os.path.join(k, ad), encoding="utf-8-sig", errors="replace") as f: satirlar = f.read().splitlines()
            except OSError: continue
            for s in satirlar:
                s = s.strip()
                if not s or s.startswith("#"): continue
                parcalar = [s] + [p.strip().strip("\"'") for p in re.split(r"[=:]", s, maxsplit=1)[1:]]
                for p in parcalar:
                    if len(p) >= 12 and not re.search(r"\s", p): gizli.add(p)
    return gizli


def _genel_deger_mi(v):
    v = v.strip().strip(",;").strip("\"'")
    if len(v) < 16 or re.search(r"[()\[\]{}<>%$]", v): return False      # kod/ifade/değişken, değer değil
    return bool(re.search(r"\d", v)) and bool(re.search(r"[A-Za-z]", v))


def tara(gelistirme, dosyalar, gizli):
    """Bulgular: [(göreli yol, satır no, tür)] — değer ASLA döndürülmez."""
    bulgu = []
    for rel in dosyalar:
        try:
            with open(os.path.join(gelistirme, rel), encoding="utf-8", errors="replace") as f: satirlar = f.read().splitlines()
        except OSError as e:
            raise RuntimeError(f"okunamadı: {rel} ({e.__class__.__name__})")
        for no, s in enumerate(satirlar, 1):
            tur = next((ad for ad, k in KALIPLAR if k.search(s)), None)
            if not tur:
                m = GENEL.search(s)
                if m and _genel_deger_mi(m.group(1)): tur = "genel_api_key"
            if not tur and HEX32.search(s) and HEX32_BAGLAM.search(s): tur = "hex_anahtar"
            if not tur and any(g in s for g in gizli): tur = "AYARLAR_anahtari"
            if tur: bulgu.append((rel, no, tur))
    return bulgu


# ---------- git ----------

def depo_denetle(depo):
    r = git(depo, "rev-parse", "--show-toplevel", kontrol=False)
    if r.returncode != 0: raise OrtamHatasi(f"git deposu değil: {depo}")
    kok = os.path.normpath(r.stdout.strip())
    if git(kok, "rev-parse", "--verify", "-q", "HEAD", kontrol=False).returncode != 0:
        raise OrtamHatasi("depoda hiç commit yok")
    if git(kok, "status", "--porcelain").stdout.strip():
        raise OrtamHatasi("depoda commit'lenmemiş değişiklik ya da izlenmeyen dosya var (önce temizle)")
    dal = git(kok, "symbolic-ref", "--short", "-q", "HEAD", kontrol=False).stdout.strip()
    if not dal: raise OrtamHatasi("depo bir dala bağlı değil (detached HEAD)")
    return kok, dal


def dal_adi(depo, ad, simdi=None):
    ad = re.sub(r"[^A-Za-z0-9._-]+", "-", ad).strip("-.") or "gelistirme"
    taban = f"yerel/{ad}-{(simdi or datetime.datetime.now()).strftime('%Y%m%d-%H%M')}"
    aday, i = taban, 2
    while git(depo, "rev-parse", "--verify", "-q", f"refs/heads/{aday}", kontrol=False).returncode == 0:
        aday, i = f"{taban}-{i}", i + 1
    return aday


def calistir(veri, depo, ad="gelistirme", kuru=False, push=True):
    gelistirme = os.path.join(veri, "GELISTIRME")
    if not os.path.isdir(gelistirme): raise OrtamHatasi(f"GELISTIRME klasörü yok: {gelistirme}")
    kok, eski_dal = depo_denetle(depo)

    alinan, atlanan = sec(gelistirme)
    print(f"GELISTIRME: {gelistirme}\nDepo: {kok} (açık dal: {eski_dal})")
    for rel, neden in atlanan: print(f"  atlandı: {rel} — {neden}")
    if not alinan:
        print("Kopyalanacak dosya yok."); return 0

    gizli = bilinen_anahtarlar([os.path.join(veri, "AYARLAR"), os.path.join(kok, "YZ_FILM", "AYARLAR")])
    bulgu = tara(gelistirme, alinan, gizli)
    del gizli
    if bulgu:
        print("\nANAHTAR BULUNDU — hiçbir şey kopyalanmadı, hiçbir şey commit'lenmedi:")
        for rel, no, tur in bulgu: print(f"  {rel}, satır {no} ({tur})")
        print("Bu satırları dosyadan çıkar (anahtar yalnız AYARLAR'da durur), sonra yeniden çalıştır.")
        return 3

    dal = dal_adi(kok, ad)
    if dal in KORUNAN_DAL or dal == eski_dal: raise RuntimeError(f"geçersiz hedef dal: {dal}")
    print(f"\nHedef dal: {dal} (yeni; {eski_dal} dalına dokunulmaz)")
    for rel in alinan: print(f"  {rel} → {hedef(rel)}")
    if kuru:
        print(f"\n[kuru] {len(alinan)} dosya taramadan geçti; hiçbir şey değiştirilmedi."); return 0

    git(kok, "checkout", "-q", "-b", dal)
    try:
        for rel in alinan:
            h = os.path.join(kok, *hedef(rel).split("/"))
            if not os.path.realpath(h).startswith(os.path.realpath(kok) + os.sep): raise RuntimeError(f"depo dışına yazılamaz: {rel}")
            os.makedirs(os.path.dirname(h), exist_ok=True)
            shutil.copyfile(os.path.join(gelistirme, *rel.split("/")), h)
        git(kok, "add", "--", *[hedef(r) for r in alinan])
        if not git(kok, "diff", "--cached", "--name-only").stdout.strip():
            print("Depodakiyle aynı; commit'lenecek değişiklik yok.")
            git(kok, "checkout", "-q", eski_dal); git(kok, "branch", "-q", "-D", dal)
            return 0
        git(kok, "commit", "-q", "-m", f"Yerel geliştirme: {ad} ({len(alinan)} dosya, esitle_gelistirme)\n\n"
            f"Kaynak: <veri>/GELISTIRME. Birleştirme bulutta PR ile (D-12).")
    except Exception:
        git(kok, "reset", "-q", "--hard", kontrol=False)
        git(kok, "checkout", "-q", eski_dal, kontrol=False)
        git(kok, "branch", "-q", "-D", dal, kontrol=False)
        git(kok, "clean", "-q", "-fd", "--", "YZ_FILM/GELISTIRME", "YZ_FILM/ARACLAR/veri/kalibrasyon", kontrol=False)
        raise
    git(kok, "checkout", "-q", eski_dal)
    print(f"Commit'lendi: {dal}")

    if not push:
        print("[push-yok] Dal yerelde kaldı; itmek için: git push -u origin " + dal); return 0
    r = git(kok, "push", "-u", "origin", dal, kontrol=False)
    if r.returncode != 0:
        print("İtilemedi (push yetkisi ya da bağlantı yok). Dosyalar GELISTIRME'de duruyor; "
              "bu klasörü bir sonraki geliştirme oturumuna ekle.")
        return 1
    print(f"İtildi: origin/{dal} — birleştirme bulut oturumunda PR ile.")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description="GELISTIRME dosyalarını ayrı dala commit'leyip iter (D-12).")
    p.add_argument("--veri", default=os.environ.get("YZ_FILM_VERI") or varsayilan_veri())
    p.add_argument("--depo", default=HERE)
    p.add_argument("--ad", default="gelistirme")
    p.add_argument("--kuru", action="store_true")
    p.add_argument("--push-yok", action="store_true")
    a = p.parse_args(argv)
    try:
        return calistir(os.path.abspath(a.veri), os.path.abspath(a.depo), a.ad, kuru=a.kuru, push=not a.push_yok)
    except OrtamHatasi as e:
        print("Ortam:", e); return 4
    except Exception as e:
        print("Hata:", e); return 1


if __name__ == "__main__":
    sys.exit(main())
