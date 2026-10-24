"""BİLDİRİM — olay tablosu, Telegram + masaüstü bildirimi (TASARIM §8.3, §8.4 "Bildirim kuralları", §6.1).

Kullanım:
  python bildirim.py --olay <olay> --metin "<metin>" [--film <film>] [--dosya <yol>] [--anahtar <tekrar anahtarı>]
  python bildirim.py --test                      Telegram ve masaüstü kanallarını dener (anahtar yazdırılmaz)
Kodda:
  import bildirim
  bildirim.gonder("bilgi_paketi", "Animatik hazır …", film=kok, dosya=mp4)   → {"gonderildi": bool, "kanallar": [...], "neden": …}
  bildirim.hatirlat(film_kok, gorev)            film.py bekle'nin 6 saatlik hatırlatması (kullanici_isi; ≤ 1 kez/6 sa)
Olaylar (§8.4): ACİL kisit_olagandisi, dogrulama, butce, kapi_tukendi · BİLGİ kullanici_isi, blok_hazir, bilgi_paketi, asama_bitti,
  oturum_ozeti, sinir_doldu, disk, hata.
Kurallar:
  - Aynı olay (+ anahtar) 30 dk içinde tekrar edilmez; bütün olaylar saatte ≤ 12 mesaj (ACİL olaylar tekrar süresine uyar ama saat
    tavanını aşabilir: Flow uyarısı hiçbir zaman susturulmaz). Durum <veri>/HESAP/BILDIRIM.jsonl'de (her deneme bir satır).
  - Mesajda gizli bilgi yok: anahtar biçimli diziler (Telegram bot anahtarı, AIza…, sk-…, uzun onaltılık), e-posta adresleri ve AYARLAR
    yolları maskelenir. Anahtar dosyası (<veri>/AYARLAR/telegram_bot.txt: 1. satır bot anahtarı, 2. satır sohbet no) yalnız kodda okunur.
  - Kanal: FILM_AYAR.json bildirim {telegram, masaustu}. Telegram yoksa/kapalıysa masaüstü (Windows balon); o da yoksa yalnız film
    klasöründeki FILM_KAYIT.txt. Dosya eki yalnız Telegram'da ve ≤ 45 MB (büyükse yolu yazılır).
  - Test kipi: YZ_FILM_BILDIRIM=sahte ya da gonder(..., kanal="sahte") → ağ yok, <veri>/HESAP/BILDIRIM_SAHTE.jsonl.
Çıkış kodları: 0 gönderildi ya da kurala göre bastırıldı · 1 kullanım/hata · 4 YOLLAR.json yok.
"""
import os, sys, re, json, time, uuid, argparse, subprocess, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "bildirim 1.0"
ACIL = ("kisit_olagandisi", "dogrulama", "butce", "kapi_tukendi")
BILGI = ("kullanici_isi", "blok_hazir", "bilgi_paketi", "asama_bitti", "oturum_ozeti", "sinir_doldu", "disk", "hata")
OLAYLAR = ACIL + BILGI
TEKRAR_SN = 30 * 60          # §8.4; eşik dosyasında anahtar yok (paylasilan_istekler: hat_esikleri bildirim_tekrar_dk)
SAAT_MAX = 12                # §8.4 "saatte ≤ 12 mesaj"
HATIRLATMA_SN = 6 * 3600     # §4.2 / §8.3: kullanıcı işinde 6 saat sonra 1 hatırlatma
EK_MAX = 45 * 1024 * 1024
GIZLI = [(re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b"), "[gizli]"), (re.compile(r"\bAIza[0-9A-Za-z_\-]{20,}\b"), "[gizli]"),
         (re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}\b"), "[gizli]"), (re.compile(r"\b[0-9a-fA-F]{32,}\b"), "[gizli]"),
         (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[e-posta]"), (re.compile(r"[^\s\"']*[\\/]AYARLAR[\\/][^\s\"']*", re.I), "[ayar dosyası]")]


def temizle(metin):
    s = str(metin or "")
    for rx, yerine in GIZLI: s = rx.sub(yerine, s)
    return s[:3500]


def _yollar():
    try: return ortak.yollar()
    except ortak.YolYok: return None


def _durum_yolu(y, ad="BILDIRIM.jsonl"): return os.path.join(y["hesap"], ad)


def _gecmis(y, son_sn=3600 * 7):
    p = _durum_yolu(y); out = []; esik = time.time() - son_sn
    try:
        with open(p, encoding="utf-8") as f:
            for s in f:
                try:
                    k = json.loads(s)
                    if k.get("t", 0) >= esik: out.append(k)
                except ValueError: continue
    except OSError: pass
    return out


def _kaydet(y, kayit, ad="BILDIRIM.jsonl"):
    os.makedirs(y["hesap"], exist_ok=True)
    with open(_durum_yolu(y, ad), "a", encoding="utf-8") as f:
        f.write(json.dumps(kayit, ensure_ascii=False) + "\n"); f.flush(); os.fsync(f.fileno())


def bastir_mi(gecmis, olay, anahtar, simdi=None):
    """(bastır, neden). Yalnız gerçekten gönderilmiş kayıtlar sayılır."""
    simdi = simdi or time.time()
    gonderilen = [k for k in gecmis if k.get("gonderildi")]
    if any(k.get("olay") == olay and k.get("anahtar") == anahtar and simdi - k.get("t", 0) < TEKRAR_SN for k in gonderilen):
        return True, "aynı olay 30 dk içinde gönderildi"
    if olay not in ACIL and sum(1 for k in gonderilen if simdi - k.get("t", 0) < 3600) >= SAAT_MAX:
        return True, "saatlik tavan (%d) doldu" % SAAT_MAX
    return False, None


def _ayar(y):
    a = ortak.json_oku(os.path.join(y["ayarlar"], "FILM_AYAR.json"), {}) or {}
    return dict({"telegram": True, "masaustu": True}, **(a.get("bildirim") or {}))


def _telegram_bilgi(y):
    p = os.path.join(y["ayarlar"], "telegram_bot.txt")
    try:
        with open(p, encoding="utf-8-sig") as f: s = [l.strip() for l in f if l.strip()][:2]
    except OSError: return None
    return s if len(s) == 2 else None


def _telegram(bilgi, metin, dosya=None):
    if dosya and os.path.isfile(dosya) and os.path.getsize(dosya) <= EK_MAX:
        sinir = uuid.uuid4().hex
        govde = b"".join([("--%s\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n%s\r\n" % (sinir, bilgi[1])).encode(),
                          ("--%s\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n" % sinir).encode() + metin[:1000].encode() + b"\r\n",
                          ("--%s\r\nContent-Disposition: form-data; name=\"document\"; filename=\"%s\"\r\nContent-Type: application/octet-stream\r\n\r\n"
                           % (sinir, os.path.basename(dosya))).encode(), open(dosya, "rb").read(), ("\r\n--%s--\r\n" % sinir).encode()])
        r = urllib.request.Request("https://api.telegram.org/bot%s/sendDocument" % bilgi[0], data=govde,
                                   headers={"Content-Type": "multipart/form-data; boundary=" + sinir})
    else:
        if dosya: metin += "\n(dosya: %s)" % dosya
        r = urllib.request.Request("https://api.telegram.org/bot%s/sendMessage" % bilgi[0],
                                   data=urllib.parse.urlencode({"chat_id": bilgi[1], "text": metin}).encode())
    with urllib.request.urlopen(r, timeout=20): pass


def _masaustu(baslik, metin):
    if os.name != "nt": return False
    ps = ("Add-Type -AssemblyName System.Windows.Forms; $n=New-Object System.Windows.Forms.NotifyIcon; "
          "$n.Icon=[System.Drawing.SystemIcons]::Information; $n.Visible=$true; "
          "$n.ShowBalloonTip(15000,'%s','%s','Info'); Start-Sleep 16; $n.Dispose()" % (baslik.replace("'", ""), metin.replace("'", "")[:200]))
    subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps], creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return True


def _kayit_dosyasi(film, satir):
    if not film or not os.path.isdir(film): return
    with open(os.path.join(film, "FILM_KAYIT.txt"), "a", encoding="utf-8") as f: f.write(satir + "\n")


def gonder(olay, metin, film=None, dosya=None, anahtar=None, kanal=None):
    if olay not in OLAYLAR: raise ValueError("bilinmeyen olay: %s (%s)" % (olay, ", ".join(OLAYLAR)))
    y = _yollar()
    if y is None: return {"gonderildi": False, "neden": "YOLLAR.json yok"}
    film_ad = os.path.basename(os.path.abspath(film)) if film else None
    m = temizle(metin); acil = olay in ACIL
    govde = ("ACİL · " if acil else "") + ("[%s] " % film_ad if film_ad else "") + m
    kanal = kanal or ("sahte" if os.environ.get("YZ_FILM_BILDIRIM") == "sahte" else None)
    anahtar = str(anahtar or film_ad or "")
    bast, neden = bastir_mi(_gecmis(y), olay, anahtar)
    kayit = {"t": time.time(), "zaman": time.strftime("%Y-%m-%dT%H:%M:%S"), "olay": olay, "anahtar": anahtar, "film": film_ad,
             "acil": acil, "gonderildi": False, "kanallar": []}
    if bast:
        kayit["neden"] = neden; _kaydet(y, kayit); return {"gonderildi": False, "neden": neden, "kanallar": []}
    if kanal == "sahte":
        kayit.update(gonderildi=True, kanallar=["sahte"]); _kaydet(y, kayit)
        _kaydet(y, {"zaman": kayit["zaman"], "olay": olay, "metin": govde, "dosya": os.path.basename(dosya) if dosya else None}, "BILDIRIM_SAHTE.jsonl")
        return {"gonderildi": True, "kanallar": ["sahte"], "metin": govde}
    a = _ayar(y); kan = []
    if a.get("telegram"):
        b = _telegram_bilgi(y)
        if b:
            try: _telegram(b, ("🚨 " if acil else "🎬 ") + govde, dosya); kan.append("telegram")
            except Exception as e: kayit["telegram_hata"] = e.__class__.__name__
    if a.get("masaustu") and (not kan or acil):
        try:
            if _masaustu("Film seti", govde): kan.append("masaustu")
        except Exception as e: kayit["masaustu_hata"] = e.__class__.__name__
    _kayit_dosyasi(film, "%s BİLDİRİM %s: %s" % (kayit["zaman"], olay, govde))
    kan.append("kayit") if film else None
    kayit.update(gonderildi=bool(kan), kanallar=kan); _kaydet(y, kayit)
    return {"gonderildi": bool(kan), "kanallar": kan}


def hatirlat(film_kok, gorev, simdi=None):
    """Kullanıcı işi 6 saattir bitmediyse 1 hatırlatma (kullanici_isi). Gönderildiyse True. gorev: GOREV.json sözlüğü."""
    simdi = simdi or time.time()
    def zaman(s):
        try:
            import datetime
            return datetime.datetime.fromisoformat(s).timestamp()
        except (TypeError, ValueError): return None
    bas = zaman((gorev.get("zaman") or {}).get("basla")) or simdi
    son = zaman(gorev.get("hatirlatma")) or bas
    if simdi - son < HATIRLATMA_SN: return False
    r = gonder("kullanici_isi", "Hatırlatma: " + str(gorev.get("mesaj") or "bekleyen bir işin var."), film=film_kok, anahtar=gorev.get("id"))
    return bool(r.get("gonderildi"))


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Bildirim gönder.")
    ap.add_argument("--olay"); ap.add_argument("--metin", default=""); ap.add_argument("--film"); ap.add_argument("--dosya")
    ap.add_argument("--anahtar"); ap.add_argument("--test", action="store_true"); ap.add_argument("--saglayici")
    o = ap.parse_args(argv)
    if _yollar() is None: print("!! YOLLAR.json yok: önce KURULUM.bat."); return 4
    if o.test:
        r = gonder("oturum_ozeti", "Film seti bildirim denemesi.", anahtar="test-%d" % int(time.time()))
        print("Bildirim denemesi: " + (", ".join(r.get("kanallar") or []) or "gönderilemedi (%s)" % r.get("neden"))); return 0
    if not o.olay: print(__doc__); return 1
    try: r = gonder(o.olay, o.metin, o.film, o.dosya, o.anahtar, "sahte" if o.saglayici == "sahte" else None)
    except ValueError as e: print("!! " + str(e)); return 1
    print(json.dumps({"gonderildi": r.get("gonderildi"), "kanallar": r.get("kanallar"), "neden": r.get("neden")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
