"""PAKETLE — seti başka bilgisayara taşınabilir zip yapar; gizli ve ağır dosyalar girmez (TASARIM §6.8, D-36).

Kullanım: python paketle.py [hedef_klasor]   (varsayılan: YOLLAR.json "masaustu", yoksa veri kökünün üstü)
  Kodda: import paketle; kod, zp = paketle.paketle(hedef) · paketle.kunye_metni() · paketle.sizinti_tara(zp)
Girer : BASLA_BURADAN.txt, KURULUM.bat, 00_BENI_OKU.txt, ARACLAR (programlar; testler/ hariç), BILGI, depodaki örnek filmler (FILMLER/ORNEK_*;
        film .bat'ları hariç: mutlak yol içerirler, alan bilgisayarda bat_yenile.py yeniden yazar), AYARLAR (yalnız boş şablonlar),
        KUNYE.txt (kaynak künyesi: veri/LISANSLAR.json'daki her bileşenin sürümü, lisansı, kaynağı ve doğrulama durumu).
Girmez: anahtar dosyalarının içeriği, Memmet Chrome profili (Google oturumu), film çıktıları, önbellekler, MEMMET_AYAR.json.
Sızıntı taraması (paket bittikten sonra, zip'in İÇİNE bakar; anahtar dosyalarının kendisi hiçbir zaman okunmaz):
  - gizli adlı girdi (…_anahtar.txt, telegram_bot.txt, .env, AYARLAR/ altında şablon dışı dosya) boş değilse,
  - memmet_profil girdisi varsa,
  - herhangi bir metinde anahtar biçimli dizi varsa (Telegram bot anahtarı, AIza…, sk-…, "-----BEGIN … PRIVATE KEY"),
  paket REDDEDİLİR: zip silinmez, gizli klasöre (<veri>/AYARLAR/_REDDEDILEN_PAKET/) taşınır ve çıkış 1 olur.
Çıkış kodları: 0 paket hazır · 1 sızıntı (paket reddedildi) ya da yazılamadı · 4 YOLLAR.json yok.
"""
import os, sys, re, json, time, shutil, zipfile, fnmatch
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)   # ROOT: depodaki YZ_FILM (paketlenen)
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

KOK = ["BASLA_BURADAN.txt", "KURULUM.bat", "00_BENI_OKU.txt"]
ATLA_KLASOR = {"__pycache__", "memmet_profil", ".git", "testler"}   # testler depoda ve CI'da koşar (sahte gizli fikstürleri var)
ATLA_ON = ("_",)                       # ARACLAR içindeki _deneme.png gibi geçici dosyalar (ARACLAR kökünde)
LISANSLAR = os.path.join(HERE, "veri", "LISANSLAR.json")
SABLONLAR = ("ai84_anahtar.txt", "telegram_bot.txt", "gemini_anahtar.txt")      # pakette BOŞ şablon olarak durur
AYAR_OKU = ("BU KLASÖR GİZLİDİR. Paylaşma.\n\n"
            "gemini_anahtar.txt → ücretsiz Gemini API anahtarını İLK SATIRA yapıştır, sonra GEMINI_TEST.bat\n"
            "ai84_anahtar.txt   → AI84.pro API anahtarını İLK SATIRA yapıştır (seslendirme)\n"
            "telegram_bot.txt   → 1. satır Telegram bot anahtarı, 2. satır sohbet no (isteğe bağlı), sonra TELEGRAM_TEST.bat\n"
            "memmet_profil\\     → FLOW_GIRIS.bat (set klasörü) ile Google'a girince kendiliğinden oluşur\n"
            "MEMMET_AYAR.json   → isteğe bağlı; Memmet temposunu yalnız YAVAŞLATABİLİR (hızlı değer yok sayılır)\n")
GIZLI_AD = ("*_anahtar.txt", "*/telegram_bot.txt", "telegram_bot.txt", "*.env", "*/.env")
ANAHTAR_DESEN = [re.compile(rb"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b"), re.compile(rb"\bAIza[0-9A-Za-z_\-]{30,}\b"),
                 re.compile(rb"\bsk-[A-Za-z0-9_\-]{20,}\b"), re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----")]
TARAMA_MAX = 5_000_000


# ---------------------------------------------------------------- künye
def kunye_metni(lisans=None):
    """KUNYE.txt: LISANSLAR.json'dan kaynak künyesi (bileşen, sürüm, kod/ağırlık lisansı, kaynak, doğrulama, YouTube'da ticari kullanım)."""
    if lisans is None:
        with open(LISANSLAR, encoding="utf-8") as f: lisans = json.load(f)
    b = lisans.get("bilesenler") or {}
    s = ["YZ FİLM SETİ — KAYNAK KÜNYESİ (veri/LISANSLAR.json'dan üretildi; paketleme tarihi " + time.strftime("%Y-%m-%d") + ")",
         "Doğrulama: 'dogrulandi' = kaynağından doğrulandı · 'bellekten' = doğrulanacak · 'bilinmiyor' = lisansı bilinmiyor "
         "(ana hatta kurulmaz, yalnız deneme).", ""]
    say = {}
    for ad in sorted(b):
        x = b[ad] or {}; d = x.get("dogrulama") or "bilinmiyor"; say[d] = say.get(d, 0) + 1
        lis = x.get("kod_lisansi") or "bilinmiyor"
        if x.get("agirlik_lisansi"): lis += f" · ağırlık: {x['agirlik_lisansi']}"
        s.append(f"- {ad}" + (f" {x['surum']}" if x.get("surum") else "") + f" — {lis}")
        s.append(f"    kaynak: {x.get('kaynak') or 'bilinmiyor'} · doğrulama: {d}"
                 + (f" ({x['dogrulama_tarihi']})" if x.get("dogrulama_tarihi") else "")
                 + f" · YouTube ticari: {x.get('ticari_youtube') or 'bilinmiyor'} · kurulum: {x.get('kurulum') or '—'}")
        if x.get("gecisli"): s.append("    dolaylı: " + ", ".join(map(str, x["gecisli"])))
    dis = {k: v for k, v in (lisans.get("dislananlar") or {}).items() if not k.startswith("_")}
    if dis:
        s += ["", "KULLANILMAYANLAR (kalite ya da lisans nedeniyle):"] + [f"- {k}: {v}" for k, v in sorted(dis.items())]
    s += ["", f"Toplam {len(b)} bileşen: " + ", ".join(f"{k} {v}" for k, v in sorted(say.items()))]
    return "\n".join(s) + "\n"


# ---------------------------------------------------------------- sızıntı taraması
def _gizli_ad(ad):
    a = ad.replace("\\", "/")
    if any(fnmatch.fnmatch(a.lower(), d) for d in GIZLI_AD): return True
    parca = a.split("/")
    if "AYARLAR" in parca:
        kalan = parca[parca.index("AYARLAR") + 1:]
        return bool(kalan) and kalan[-1] != "OKU_BENI.txt"
    return False


def sizinti_tara(zp):
    """Zip girdilerinde sızıntı listesi [(girdi, neden)]; boşsa temiz. Anahtar dosyaları açılmaz: yalnız zip'in içi okunur."""
    out = []
    with zipfile.ZipFile(zp) as z:
        for i in z.infolist():
            ad = i.filename
            if "memmet_profil" in ad: out.append((ad, "Google profili")); continue
            if _gizli_ad(ad) and i.file_size > 0: out.append((ad, "gizli dosya boş değil")); continue
            if i.file_size < TARAMA_MAX:
                data = z.read(ad)
                if any(r.search(data) for r in ANAHTAR_DESEN): out.append((ad, "anahtar biçimli dizi"))
    return out


# ---------------------------------------------------------------- paket
def _hedef_varsayilan():
    y = ortak.yollar(); return y.get("masaustu") or os.path.dirname(y["veri_kok"])


def paketle(hedef=None, yaz=print):
    Y = ortak.yollar()
    hedef = os.path.abspath(hedef or _hedef_varsayilan()); os.makedirs(hedef, exist_ok=True)
    zp = os.path.join(hedef, f"YZ_FILM_PAKET_{time.strftime('%Y-%m-%d_%H%M%S')}.zip"); tmp = zp + ".part"
    n = 0
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        def ekle(src, arc):
            nonlocal n; z.write(src, "YZ_FILM/" + arc.replace("\\", "/")); n += 1

        def yaz_(arc, metin):
            nonlocal n; z.writestr("YZ_FILM/" + arc, metin); n += 1
        for f in KOK:
            if os.path.exists(os.path.join(ROOT, f)): ekle(os.path.join(ROOT, f), f)
        for top in ("ARACLAR", "BILGI"):
            for dp, dns, fns in os.walk(os.path.join(ROOT, top)):
                dns[:] = sorted(d for d in dns if d not in ATLA_KLASOR)
                for f in sorted(fns):
                    if f.endswith((".pyc", ".part", ".tmp")) or f == "MEMMET_AYAR.json": continue
                    if top == "ARACLAR" and dp == os.path.join(ROOT, "ARACLAR") and f.startswith(ATLA_ON): continue
                    p = os.path.join(dp, f); ekle(p, os.path.relpath(p, ROOT))
        filmler = os.path.join(ROOT, "FILMLER")
        for ad in sorted(os.listdir(filmler)) if os.path.isdir(filmler) else []:
            if not ad.startswith("ORNEK_"): continue
            for dp, dns, fns in os.walk(os.path.join(filmler, ad)):
                dns[:] = sorted(d for d in dns if d not in ATLA_KLASOR)
                for f in sorted(fns):
                    if f.lower().endswith(".bat") or f.endswith((".pyc", ".part", ".tmp")): continue
                    p = os.path.join(dp, f); ekle(p, os.path.relpath(p, ROOT))
        yaz_("AYARLAR/OKU_BENI.txt", AYAR_OKU)
        for f in SABLONLAR: yaz_("AYARLAR/" + f, "")
        yaz_("KUNYE.txt", kunye_metni())
    siz = sizinti_tara(tmp)
    if siz:
        red = os.path.join(Y["ayarlar"], "_REDDEDILEN_PAKET"); os.makedirs(red, exist_ok=True)
        shutil.move(tmp, os.path.join(red, os.path.basename(zp)))
        yaz("!! GÜVENLİK: pakete gizli bilgi girmiş; paket REDDEDİLDİ (silinmedi, gizli AYARLAR klasörüne taşındı):")
        for ad, neden in siz[:20]: yaz(f"   {ad}: {neden}")
        return 1, None
    os.replace(tmp, zp)
    yaz(f"PAKET: {zp}\n  {n} dosya · {os.path.getsize(zp) / 1e6:.1f} MB · künye: KUNYE.txt")
    yaz("  Güvenlik taraması temiz: anahtar ve Google oturumu pakette yok.")
    return 0, zp


def main(a=None):
    a = sys.argv[1:] if a is None else list(a)
    try: kod, _ = paketle(a[0] if a else None)
    except ortak.YolYok as e: print("!!", e); return 4
    except OSError as e: print("!! paket yazılamadı:", e); return 1
    return kod


if __name__ == "__main__":
    sys.exit(main())
