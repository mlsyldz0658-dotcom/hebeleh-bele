"""MEMMET AUTO — Google Flow'da görsel ve video üretimi (v1: SAHNELER partileri · v2: BLOK_PLANI blokları).

Kullanım:
  python memmet.py <film_klasoru> --giris            Memmet Chrome'unu açar; Google'a bir kez sen giriş yaparsın
  python memmet.py <film_klasoru> --bakiye           Flow kredi bakiyesini salt okur (gönderim yok) → HESAP/FLOW_BAKIYE.json
  v2 (SAHNELER "_surum" ≥ 2; yalnız film.py / VIDEO_*.bat üzerinden):
  python memmet.py <film_klasoru> --blok <BLOK_PLANI.json#B03 | B03 | sonraki> --onizleme <imza> [--mod elle|gece]
        bir bloğu (≤ 20 plan) gönderir. İmza = blok_plani.py --imza (kesin bütçe BUT2'nin imzası; FILM_DURUM'da animatik ONAYLI).
        Bloksuz, imzasız ya da imzası tutmayan v2 dosyasında hiçbir şey göndermez (4).
  v1 (eski SAHNELER; saglayicilar/flow.py):
  python memmet.py <film_klasoru>                    bütün partilerin görselleri (v1'de video gönderimi YOK: animatik imzası
                                                     ve bütçe noktası v1'de yok; --asama video → 4, film v2'ye taşınır)
  python memmet.py <film_klasoru> --asama gorsel     yalnız görseller
  python memmet.py <film_klasoru> --parti 1,2        yalnız bu partiler  (--sahne 3,7: yalnız bu sahneler)
  Ortak: --mod elle   (varsayılan) Memmet istemi hazırlar, GÖNDER'e (Oluşturmaya başla) SEN basarsın
         --mod gece   Memmet kendisi gönderir; yalnız FILM_AYAR.json "izinler.gece_flow": true ise. "Gündüz otomatik" kip YOK.
         --film <film_klasoru> (film.py araç sözleşmesi) · --telegram-test (telefona deneme mesajı)

Kendi Chrome profiliyle (memmet_profil) gerçek Chrome'u açar ve ona bağlanır; senin diğer oturumlarına dokunmaz.
Ekran görüntüsüne bakmaz, sayfanın yapısını okur. Her sonucu Flow'daki istem metninden tanıyıp NNN.jpg / NNN.mp4 olarak kaydeder.
Yük sınırı: gönderimler arası bekleme ve molalar kodda sabittir (17.10 değerleri); MEMMET_AYAR.json yalnız YAVAŞLATABİLİR.
Son gönderim zamanı ve kalan mola HESAP/FLOW_TEMPO.json'da tutulur; Memmet'i kapatıp açmak molayı sıfırlamaz.
v2 her gönderimden önce: FLOW_TEMPO/FLOW_YUK (flow_yuk), <film>/DUR, plan uygunluğu (G1 sha'sı, zincir kaynağı, kaynak_klip, soy ≤ 3,
toplanmamış gönderim) ve bütçe noktası BUTK; sonra kredi defterine gönderim satırı (KREDI_DEFTERI.jsonl) ÖNCE yazılır.
Filtre reddinde aynı istem yeniden gönderilmez: derlenmiş yedek istem bir kez, sonra plan yonetmen·onarim'a (_RAPOR/FLOW_<blok>.json).
Zaman aşımında yeniden gönderilmez: önce toplanır (memmet_topla.py). Hesap e-postasının yalnız sha1'i tutulur (HESAP_DURUMU.json).
Aynı Flow hesabında ikinci Memmet açılmaz (HESAP/FLOW.kilit; 8). Kilit arka planda ve her beklemede tazelenir; sahibi yaşıyorsa
(Windows'ta OpenProcess ile) kaldırılmaz.

GÜVENLİK (bot tespiti atlatılmaz; 03_DERSLER.md):
  - Flow "olağan dışı etkinlik" derse, HER KİPTE anında durur: sayfada başka hiçbir işlem yapmaz (tıklama, yazma, yenileme yok),
    HESAP/FLOW_KILIDI.json yazar, haber verir ve 7 ile çıkar. Kilit varken Memmet açılmaz. GÖNDER'e basma, sayfayı yenileme.
    Sayfayı değiştiren HER çağrı tek kapıdan geçer (Memmet.dokun): hemen önce sayfanın TAM metni ve uyarı kutuları (role=alert/dialog,
    aria-live, açık shadow kökleri) okunur; uyarı bir kez görüldüyse hiçbir işlem yapılmaz; işlem hata verirse (uyarı katmanı tıklamayı
    engelleyip zaman aşımı) önce uyarı yeniden okunur. Uzun beklemeler dilimlenir: her dilimde uyarı okunur (≤ 10 sn'de dur).
    v1 (eski SAHNELER) filmlerde video gönderimi YOK (yalnız görsel); zaman aşımında hiçbir sürümde yeniden gönderilmez.
  - reCAPTCHA, doğrulama ya da oturum düşmesinde beklemez, kendiliğinden sürmez: haber verir ve 2 ile çıkar.
    Sen çözersin, sonra Memmet'i yeniden başlatırsın.
  - SAHNELER.json "_surum" ≥ 2 ise --blok ve --onizleme olmadan hiçbir şey yapmaz, 4 ile çıkar.
Çıkış kodları: 0 bitti · 1 beklenmeyen hata · 2 durdu (doğrulama/giriş/kredi/arayüz/DUR) · 4 ortam/sürüm/imza · 5 bütçe ·
               7 Flow uyarısı ya da kilit · 8 bekle (toplanacak iş, başka Memmet açık).
Son çıkışın nedeni film klasöründe _memmet_cikis.json'a yazılır. Her şey MEMMET_KAYIT.txt'ye, durum MEMMET_DURUM.json'a yazılır.

MEMMET3 AKTARIMI (ilk yerel oturum, 24.10.2026): bu dosya depodaki PR-0 yamalı memmet.py'nin üstüne memmet3'ün (CLAUDE KANALI\memmet3,
19.10) güvenli eklerini taşır: MEMMET_AYAR "video_model" (sahnede "video_model" önce gelir; seçim dokun() ile), "gorsel_adet" 1|2 (x2:
istem başına 2 aday, ek aday NNN_b.jpg), SAHNELER "en_boy" (16:9 | 9:16), elle kipte karakter referansı sahnesi gelince tek tek yüklenir,
Chrome arka plan yavaşlatma bayrakları ve MEMMET_OLCEK. ALINMAYANLAR (D-02, D-03, D-04): --hesap (başka Flow hesabı), --telefon (beklemeden
P sahne art arda), elle/telefon kipinde beklemeyi kısaltma, uyarıda sayfa yenileme / "F5 sonra devam", MEMMET_KONUM çoklu pencere.
"""
import os, sys, re, json, time, datetime, random, shutil, socket, subprocess, urllib.request, urllib.parse, traceback, ctypes, hashlib
import threading
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ortak
try: _Y = ortak.yollar()                     # yollar yalnız YOLLAR.json'dan (kurulum.py --yollar)
except ortak.YolYok as e:
    if __name__ == "__main__": print("!!", e); sys.exit(4)
    raise
VERI = _Y["veri_kok"]
AYARLAR = _Y["ayarlar"]
AYAR_DOSYA = os.path.join(AYARLAR, "MEMMET_AYAR.json")
FILM_AYAR = os.path.join(AYARLAR, "FILM_AYAR.json")
HESAP = _Y["hesap"]                          # hesap düzeyindeki durum: tempo ve kilit (filmden bağımsız)
import flow_yuk                              # hesap düzeyi yük: FLOW_YUK.jsonl, FLOW_TEMPO, kilit, günlük tavanlar
import blok_plani, kredi                     # v2: uygunluk, imza, blok işaretleri · bütçe noktası ve kredi defteri
import kare_denetim                          # v2: her video gönderiminden önce video_hazir (G1 GEÇ + SHA1)
import animatik_imza                         # v2: animatik imzası her blokta yeniden doğrulanır (FILM_DURUM önbelleğine güvenilmez)


def chrome_bul():
    for p in (os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
              r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
        if os.path.exists(p): return p
    return "chrome.exe"


def telegram_bul():
    for p in (os.path.join(AYARLAR, "telegram_bot.txt"), os.path.join(os.path.expanduser("~"), "Desktop", "telegram_bot.txt")):
        if os.path.exists(p) and open(p, encoding="utf-8-sig").read().strip(): return p
    return os.path.join(AYARLAR, "telegram_bot.txt")


# Bilgisayara özel yollar (chrome, profil, telegram) her çalıştırmada bulunur
VARSAYILAN = {
    "chrome": chrome_bul(),
    "profil": os.path.join(AYARLAR, "memmet_profil"),
    "port": 9333,                       # sabit: ayar dosyasından alınmaz (başka Chrome/profil gösterilemez)
    "gorsel_zaman_asimi_sn": 180,
    "video_zaman_asimi_sn": 360,
    "video_cozunurluk": "720p",
    "video_sure": "8 sn.",
    "video_model": None,                # memmet3: ör. "Omni 1.1 Flash" / "Veo 3.1 - Lite"; None = Flow'da seçili model
    "gorsel_adet": 1,                   # memmet3: 1 | 2 (istem başına aday)
    "telegram_dosya": telegram_bul(),   # 1. satır bot anahtarı, 2. satır sohbet no
}
# Yük sınırı (17.10 değerleri). Kodda sabit; ayar dosyası bunları yalnız YAVAŞLATABİLİR (sikilastir).
#   gonderim_arasi_sn   iki gönderim arası rastgele bekleme      ayni_anda           aynı anda en fazla kaç üretim beklesin
#   mola_kac_gonderimde N gönderimde bir mola (0: yok)           mola_kac_partide    N partide bir mola (0: yok)
TEMPO = {
    "elle": {"gonderim_arasi_sn": [6, 15], "ayni_anda": 2, "mola_kac_gonderimde": 8, "gonderim_mola_dk": [3, 6],
             "mola_kac_partide": 0, "parti_mola_dk": [0, 0]},
    "gece": {"gonderim_arasi_sn": [12, 30], "ayni_anda": 2, "mola_kac_gonderimde": 0, "gonderim_mola_dk": [0, 0],
             "mola_kac_partide": 2, "parti_mola_dk": [15, 30]},
}
KIPLER = tuple(TEMPO)
KALKAN_KIPLER = ("gunduz", "gündüz", "gunduz_otomatik", "otomatik")   # BK §6.2 #7: gündüz otomatik kip 15–20 dk'da uyarı aldı; yok
FLOW = "https://flow.google.com/"
# Olağan dışı etkinlik: HER KİPTE anında dur, sayfaya dokunma (çıkış 7). Bu liste yalnız BÜYÜYEBİLİR.
OLAGANDISI_KELIMELERI = ["olağandışı etkinlik", "olağan dışı etkinlik", "olagandisi etkinlik", "olagan disi etkinlik",
                         "unusual traffic", "unusual activity", "olağandışı trafik", "olağan dışı trafik"]
# Tek sonuç kartındaki üretim hatası (yeniden denenebilir). "olağan/unusual" BURADA YOK: onlar uyarıdır, hata değil.
HATA_KELIMELERI = ["politika", "ihlal", "uygunsuz", "güvenlik", "başarısız", "oluşturulamadı",
                   "üretilemedi", "violat", "policy", "couldn't", "could not", "failed", "something went wrong",
                   "bir sorun", "bir hata"]
# Doğrulama / robot sorusu: beklemeden dur (çıkış 2). "doğrulayın" tek başına yazılmaz: Flow'un altında hep "yanıtları doğrulayın" yazıyor
DOGRULAMA_KELIMELERI = ["robot olmadığınızı", "not a robot", "kimliğinizi doğrulayın", "verify it's you"]
KREDI_KELIMELERI = ["yetersiz kredi", "kredi yetersiz", "kredin bitti", "not enough credits", "out of credits", "insufficient credits"]
# Politika/filtre reddi (v2): aynı istem yeniden gönderilmez; derlenmiş yedek bir kez, sonra yonetmen·onarim. HATA_KELIMELERI'nin alt kümesi.
FILTRE_KELIMELERI = ["politika", "ihlal", "uygunsuz", "violat", "policy"]
CIKIS = {"tamam": 0, "beklenmeyen": 1, "dogrulama": 2, "giris": 2, "kredi": 2, "arayuz": 2, "genel": 2, "ortam": 4, "surum": 4,
         "olagandisi": 7, "kilitli": 7, "yuk": 2, "dur": 2, "imza": 4, "butce": 5, "topla": 8, "mesgul": 8, "hesap": 2}
FLOW_KILIT_BAYAT_SN = 1800        # HESAP/FLOW.kilit: sahibi 30 dk tazelemediyse bayat (UM2 §4.2.1)
FLOW_KILIT_TAZELE_SN = 60         # sahibi kilidi arka planda bu sıklıkla tazeler (uzun beklemede de)
UYKU_DILIM_SN = 2                 # uzun beklemeler bu dilimlerle uyunur; her dilimde uyarı okunur (uyarıdan ≤ 10 sn'de dur)
YAZMA_GECIKMESI_MS = 12           # istem yazma gecikmesi SABİT (rastgele değil: "insan taklidi" yok; yalnız arayüzün yetişmesi için)
YAZMA_PARCA = 24                  # istem parça parça yazılır; her parçadan önce uyarı okunur
ISLEM_ZAMAN_ASIMI_MS = 7000       # tıklama/yazma bekleme sınırı: uyarı katmanı tıklamayı engellerse hata ≤ 7 sn'de gelir, uyarı okunur
GEZINME_ZAMAN_ASIMI_MS = 30000
UYARI_MESAJI = "Flow uyarı verdi (olağan dışı etkinlik): GÖNDER'e basma, sayfayı yenileme. Memmet durdu; Claude'a haber ver."
# Sayfa metni: gövdenin TAMAMI (kesme yok) + uyarı kutuları (role=alert/alertdialog/dialog/status, aria-live, <dialog>, aria-modal)
# + açık shadow kökleri. İşaret (memmet:metin) yalnız testlerin sahte sayfası içindir.
METIN_JS = r"""() => { /*memmet:metin*/
  const out = [document.body ? (document.body.innerText || '') : ''];
  const sec = '[role=alert],[role=alertdialog],[role=dialog],[role=status],[aria-live],dialog,[aria-modal=true]';
  const gez = (kok, d) => {
    if (!kok || d > 8) return;
    for (const e of kok.querySelectorAll(sec)) out.push(e.innerText || '', e.textContent || '', (e.getAttribute && e.getAttribute('aria-label')) || '');
    for (const e of kok.querySelectorAll('*')) {
      if (e.shadowRoot) { for (const c of e.shadowRoot.children || []) out.push(c.innerText || c.textContent || ''); gez(e.shadowRoot, d + 1); }
    }
  };
  gez(document, 0);
  return out.join('\n');
}"""
# oku() bu JS'leri reddeder: sayfayı değiştiren JS yalnız dokun() ile
DEGISTIREN_JS = re.compile(r"dispatchEvent|\.click\s*\(|scroll(?:To|By|IntoView)|appendChild|removeChild|insertBefore|replaceChild|"
                           r"\.remove\s*\(|\.focus\s*\(|\.blur\s*\(|\.value\s*=[^=]|innerHTML\s*=|outerHTML\s*=|textContent\s*=[^=]|"
                           r"\.submit\s*\(|setAttribute|location\s*=[^=]|location\.(?:assign|replace|reload)|history\.|\.play\s*\(|"
                           r"\.pause\s*\(|execCommand|\.requestSubmit|\.showModal|\.close\s*\(")


def _yavas(kod, gelen):
    """İki değerden yavaş (güvenli) olanı. Aralıklar eleman eleman büyük; ayni_anda küçük; mola sıklığı küçük (0 = yok sayılır)."""
    try:
        if isinstance(kod, list):
            g = [float(x) for x in gelen][:len(kod)]
            return [max(a, b) for a, b in zip(kod, g)] if len(g) == len(kod) else kod
        g = int(gelen)
        if kod == 0: return 0                                # kodda kapalı olan mola sıklığı ayarla açılmaz (gece/elle farkı)
        return min(kod, g) if g > 0 else kod
    except (TypeError, ValueError): return kod


def sikilastir(kip, dosya_ayar):
    """Kodda sabit tempo + ayar dosyası → yalnız yavaşlayan birleşim."""
    t = {k: (list(v) if isinstance(v, list) else v) for k, v in TEMPO[kip].items()}
    for k in t:
        if k in dosya_ayar: t[k] = _yavas(t[k], dosya_ayar[k])
    return t


def ayar(kip="elle"):
    """VARSAYILAN + tempo. Tempo = kodda sabit TEMPO, MEMMET_AYAR.json ve flow_yuk.tempo (hat_esikleri + FILM_AYAR + KURALLAR_OGRENILEN
    + UYARI_GECTI günü çarpanı) — üçünden de yalnız YAVAŞ olan. Zaman aşımları kod değerinden kısaltılamaz; port ayardan alınmaz."""
    a = dict(VARSAYILAN)
    d = {}
    if os.path.exists(AYAR_DOSYA):
        try: d = json.load(open(AYAR_DOSYA, encoding="utf-8-sig"))
        except ValueError: d = {}
    if not isinstance(d, dict): d = {}
    # eski (sürümsüz) dosyayı eski Memmet kendiliğinden yazmıştı (360p, hızlı tempo): ondan yalnız yavaşlatan tempo alınır
    if int(d.get("_surum", 1) or 1) >= 2:
        for k in ("gorsel_zaman_asimi_sn", "video_zaman_asimi_sn"):          # yalnız uzar (kısa zaman aşımı = daha erken yeniden deneme)
            try:
                if k in d: a[k] = max(VARSAYILAN[k], int(d[k]))
            except (TypeError, ValueError): pass
        if "video_cozunurluk" in d: a["video_cozunurluk"] = d["video_cozunurluk"]
        if a["video_cozunurluk"] not in ("720p", "1080p"): a["video_cozunurluk"] = "720p"   # en az 720p
    # memmet3 ekleri: tempoya dokunmaz; yalnız arayüz seçimi (sürümsüz memmet3 dosyasından da okunur)
    if isinstance(d.get("video_model"), str) and 0 < len(d["video_model"]) <= 60: a["video_model"] = d["video_model"]
    if d.get("gorsel_adet") in (1, 2): a["gorsel_adet"] = d["gorsel_adet"]
    t = sikilastir(kip, d)
    try: ft = flow_yuk.tempo(kip, kok=HESAP, ek={k: v for k, v in t.items()})
    except Exception as e:                                                   # eşikler okunamazsa gönderim yok (kapalı başarısız)
        raise Durdur(f"Flow tempo eşikleri okunamadı ({str(e)[:120]}): gönderim yapılmadı.", kod="ortam")
    for k in t:
        if k in ft: t[k] = _yavas(t[k], ft[k])
    a.update(t); a["kip"] = kip
    return a


def gece_izni():
    try: return bool(json.load(open(FILM_AYAR, encoding="utf-8-sig")).get("izinler", {}).get("gece_flow"))
    except (OSError, ValueError, AttributeError): return False


def kilit_yolu(): return os.path.join(HESAP, "FLOW_KILIDI.json")


def tempo_yolu(): return os.path.join(HESAP, "FLOW_TEMPO.json")


uyu = time.sleep   # testler bekleme yapmadan koşabilsin diye tek noktadan


def _atomik(yol, veri):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False, indent=1)
    os.replace(tmp, yol)


def cikis_yaz(root, kod, mesaj, ek=None):
    """Son çıkışın nedeni: film.py / saglayicilar.flow kodu buradan okur. ek: v2 blok özeti (gonderilen, indirilen, bekleyen …)."""
    v = {"kod": kod, "cikis": CIKIS.get(kod, 1), "mesaj": mesaj, "zaman": time.strftime("%Y-%m-%d %H:%M:%S")}
    for k, x in (ek or {}).items(): v.setdefault(k, x)
    try: _atomik(os.path.join(root, "_memmet_cikis.json"), v)
    except OSError: pass


def flow_kilit_yolu(): return os.path.join(HESAP, "FLOW.kilit")


def _pid_yasiyor_nt(pid, k32=None, son_hata=None):
    """Windows: OpenProcess + GetExitCodeProcess (os.kill Windows'ta süreci öldürür: kullanılmaz). Erişim reddi → yaşıyor sayılır."""
    try:
        k32 = k32 or ctypes.windll.kernel32
        son_hata = son_hata or (lambda: ctypes.GetLastError())
        h = k32.OpenProcess(0x1000, False, int(pid))                 # PROCESS_QUERY_LIMITED_INFORMATION
        if not h: return son_hata() == 5                               # ERROR_ACCESS_DENIED: süreç var
        try:
            kod = ctypes.c_ulong(0)
            if not k32.GetExitCodeProcess(h, ctypes.byref(kod)): return True
            return kod.value == 259                                    # STILL_ACTIVE
        finally: k32.CloseHandle(h)
    except Exception: return True                                      # ölçülemedi: yaşıyor sayılır (kilit kalkmaz)


def _pid_yasiyor(pid):
    if os.name == "nt": return _pid_yasiyor_nt(pid)
    try: os.kill(pid, 0); return True
    except ProcessLookupError: return False
    except OSError: return True


_KILIT = {"dur": None, "kilit": threading.Lock()}


def _tazeleyici_baslat():
    """Kilidin sahibi yaşadığı sürece kilit tazelenir (uzun bekleme, alt süreç, Playwright beklemesi sırasında da)."""
    _tazeleyici_durdur()
    dur = threading.Event(); _KILIT["dur"] = dur
    def dongu():
        while not dur.wait(FLOW_KILIT_TAZELE_SN): flow_kilidi_tazele()
    threading.Thread(target=dongu, name="FLOW.kilit tazeleyici", daemon=True).start()


def _tazeleyici_durdur():
    if _KILIT["dur"] is not None: _KILIT["dur"].set(); _KILIT["dur"] = None


def flow_kilidi_al(film):
    """Aynı Flow hesabında tek Memmet (HESAP/FLOW.kilit). Alınamazsa Durdur(mesgul) → 8. Bayat kilit (sahibi yok ya da 30 dk
    tazelenmemiş) kaldırılır. FLOW_KILIDI.json (uyarı kilidi) bundan ayrıdır ve yalnız UYARI_GECTI.bat ile kalkar."""
    p = flow_kilit_yolu(); os.makedirs(HESAP, exist_ok=True)
    for _ in range(2):
        try:
            fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as f: json.dump({"pid": os.getpid(), "zaman": time.time(), "film": film}, f)
            _tazeleyici_baslat()
            return True
        except FileExistsError:
            try: k = json.load(open(p, encoding="utf-8"))
            except (OSError, ValueError): k = {}
            pid = k.get("pid"); yas = time.time() - float(k.get("zaman") or 0)
            if pid == os.getpid() or not isinstance(pid, int) or not _pid_yasiyor(pid) or yas > FLOW_KILIT_BAYAT_SN:
                try: os.remove(p)
                except OSError: pass
                continue
            raise Durdur(f"Aynı Flow hesabında başka bir Memmet çalışıyor (film {k.get('film')}). İki film aynı anda Flow'a gidemez; "
                         "o bitince yeniden başlat.", kod="mesgul")
    raise Durdur("FLOW.kilit alınamadı.", kod="mesgul")


def flow_kilidi_tazele():
    p = flow_kilit_yolu()
    with _KILIT["kilit"]:
        try:
            k = json.load(open(p, encoding="utf-8"))
            if k.get("pid") == os.getpid(): k["zaman"] = time.time(); _atomik(p, k)
        except (OSError, ValueError): pass


def flow_kilidi_birak():
    _tazeleyici_durdur()
    p = flow_kilit_yolu()
    try:
        if json.load(open(p, encoding="utf-8")).get("pid") == os.getpid(): os.remove(p)
    except (OSError, ValueError): pass


def kilit_yaz(film, mesaj):
    """Flow uyarısı → hesap düzeyinde kilit (flow_yuk.uyari_kaydet). Aynı takvim haftasında ikinci uyarı → en erken 7 gün sonra."""
    return flow_yuk.uyari_kaydet(film, mesaj, kok=HESAP)


def norm(s): return re.sub(r"\s+", " ", (s or "")).strip().lower()


class Durdur(BaseException):
    """Kullanıcının müdahalesi gereken durum. kod: olagandisi | kilitli | dogrulama | giris | kredi | arayuz | ortam | surum | genel.
    BaseException'dan türer: hiçbir `except Exception` (yükleme, seçici, hover denemeleri …) bir durdurmayı yutamaz."""
    def __init__(self, msg, kod="genel"):
        super().__init__(msg); self.kod = kod


class Memmet:
    def __init__(self, root, args):
        self.root = os.path.abspath(root); self.args = args
        kip = args.get("mod", "elle")
        if kip in KALKAN_KIPLER: raise Durdur(f"'{kip}' kipi kaldırıldı (Flow uyarısı aldı). Kipler: elle (varsayılan) | gece", kod="ortam")
        if kip not in KIPLER: raise Durdur(f"Bilinmeyen kip: {kip} (elle | gece)", kod="ortam")
        self.A = ayar(kip)
        self.plan = json.load(open(os.path.join(self.root, "SAHNELER.json"), encoding="utf-8-sig"))
        self.v2 = int(self.plan.get("_surum", 1) or 1) >= 2
        gonderimsiz = args.get("giris") or args.get("bakiye") or args.get("topla")
        if self.v2 and not gonderimsiz and not (args.get("blok") and args.get("onizleme")):
            raise Durdur("SAHNELER.json v2 (_surum ≥ 2): Memmet yalnız --blok <BLOK_PLANI> --onizleme <imza> ile gönderir "
                         "(film.py / VIDEO_*.bat). Hiçbir şey yapılmadı.", kod="surum")
        if args.get("blok") and not self.v2: raise Durdur("--blok yalnız SAHNELER v2 ile çalışır.", kod="surum")
        self.film = self.plan["film"]
        self.sg = os.path.join(self.root, "SIRALI_GORSEL"); self.sv = os.path.join(self.root, "SIRALI_VIDEO")
        self.hata_dir = os.path.join(self.root, "_MEMMET_HATALAR"); self.gecici = os.path.join(self.root, "_memmet_gecici")
        for d in (self.sg, self.sv, self.hata_dir, self.gecici): os.makedirs(d, exist_ok=True)
        self.kayit = open(os.path.join(self.root, "MEMMET_KAYIT.txt"), "a", encoding="utf-8")
        self.dp = os.path.join(self.root, "MEMMET_DURUM.json")
        self.D = json.load(open(self.dp, encoding="utf-8")) if os.path.exists(self.dp) else {"proje_url": None, "yuklenen": [], "sahne": {}}
        self.page = None; self._tg = None; self.uyari_goruldu = False
        self.D.setdefault("isler", {}); self.blok = None; self.ozet = None; self.hesap = None; self._tazele = 0

    # ------------------------------------------------------------------ kayıt ve bildirim
    def log(self, *a):
        line = time.strftime("%d.%m %H:%M:%S ") + " ".join(str(x) for x in a)
        print(line, flush=True); self.kayit.write(line + "\n"); self.kayit.flush()

    def save(self): _atomik(self.dp, self.D)

    def sc(self, n): return self.D["sahne"].setdefault(str(n), {})

    def telegram(self):
        if self._tg is None:
            p = self.A.get("telegram_dosya")
            self._tg = [l.strip() for l in open(p, encoding="utf-8-sig") if l.strip()][:2] if p and os.path.exists(p) else []
        return self._tg if len(self._tg) == 2 else None

    def bildir(self, msg, acil=False):
        self.log("BİLDİRİM:", msg)
        try:
            import winsound
            for _ in range(3 if acil else 1): winsound.MessageBeep(winsound.MB_ICONEXCLAMATION); time.sleep(0.4)
        except Exception: pass
        try:   # Windows balon bildirimi
            ps = ("Add-Type -AssemblyName System.Windows.Forms; $n=New-Object System.Windows.Forms.NotifyIcon; "
                  "$n.Icon=[System.Drawing.SystemIcons]::Information; $n.Visible=$true; "
                  f"$n.ShowBalloonTip(15000,'Memmet Auto','{msg.replace(chr(39), '')[:200]}','Info'); Start-Sleep 16; $n.Dispose()")
            subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except Exception: pass
        tg = self.telegram()
        if tg:
            try:
                data = urllib.parse.urlencode({"chat_id": tg[1], "text": ("🚨 " if acil else "🎬 ") + f"[{self.film}] {msg}"}).encode()
                urllib.request.urlopen(f"https://api.telegram.org/bot{tg[0]}/sendMessage", data, timeout=5)
            except Exception as e: self.log("telegram gönderilemedi:", str(e)[:80])

    # ------------------------------------------------------------------ Chrome
    def chrome_ac(self):
        port = self.A["port"]
        def acik():
            with socket.socket() as s:
                s.settimeout(1); return s.connect_ex(("127.0.0.1", port)) == 0
        if not acik():
            os.makedirs(self.A["profil"], exist_ok=True)
            subprocess.Popen([self.A["chrome"], f"--remote-debugging-port={port}", f"--user-data-dir={self.A['profil']}",
                              "--no-first-run", "--no-default-browser-check", "--start-maximized",
                              # memmet3: pencere arkada kalınca Chrome yavaşlatmasın (sayfaya dokunmaz)
                              "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding",
                              "--disable-background-timer-throttling"]
                             + ([f"--force-device-scale-factor={os.environ['MEMMET_OLCEK']}"] if os.environ.get("MEMMET_OLCEK") else [])
                             + [FLOW])
            for _ in range(60):
                if acik(): break
                time.sleep(1)
            else: raise Durdur("Memmet Chrome'u açılamadı.")
        from playwright.sync_api import sync_playwright
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        ctx = self.browser.contexts[0]
        self.page = next((p for p in ctx.pages if "flow.google.com" in p.url), None) or (ctx.pages[0] if ctx.pages else ctx.new_page())
        self.page.set_default_timeout(ISLEM_ZAMAN_ASIMI_MS)
        self.page.set_default_navigation_timeout(GEZINME_ZAMAN_ASIMI_MS)
        self.log("Chrome bağlandı.")

    def kapat(self):
        try: self.pw.stop()
        except Exception: pass

    # ------------------------------------------------------------------ güvenlik: tek okuma ve tek dokunma kapısı
    def oku(self, js, *a):
        """Salt okuma JS'i. Sayfayı değiştiren JS (olay gönderme, tıklama, kaydırma, DOM ekleme …) burada reddedilir: o yalnız dokun() ile."""
        if DEGISTIREN_JS.search(js): raise RuntimeError("oku() yalnız okur; sayfayı değiştiren JS dokun() ile çağrılır")
        return self.page.evaluate(js, *a)

    def dokun(self, islem, *a, _giris=False, **k):
        """Sayfayı DEĞİŞTİREN her çağrının (tıklama, yazma, tuş, gezinme, fare, dosya, olay gönderen/kaydıran JS) tek kapısı.
        Hemen önce tam kontrol noktası (uyarı: tam metin + uyarı kutuları; doğrulama; kredi). Uyarı bir kez görüldüyse hiçbir işlem
        yapılmaz. İşlem hata verirse (ör. uyarı katmanı tıklamayı engelledi, zaman aşımı) önce uyarı yeniden okunur: varsa Durdur(7)."""
        if self.uyari_goruldu: raise Durdur(UYARI_MESAJI, kod="olagandisi")
        self.kontrol_noktasi(giris=_giris, son=True)          # son okuma = sayfa metni; ondan sonra yalnız işlemin kendisi
        try: return islem(*a, **k)
        except Exception:
            self.olagandisi_denetle()
            raise

    def sayfa_metni(self, son=False):
        """Sayfanın TAM metni (kesme yok) + uyarı kutuları; normalleştirilmiş. Okunamazsa None (gezinme sırasında 3 deneme).
        son=True: dokun()'un işlemden hemen önceki son okuması (aynı JS; işaret yalnız testlerin sahte sayfası için)."""
        js = METIN_JS.replace("/*memmet:metin*/", "/*memmet:metin son*/") if son else METIN_JS
        for deneme in range(3):
            try:
                t = self.oku(js)
                return norm(t if isinstance(t, str) else "")
            except Exception:
                if deneme < 2: uyu(0.5)
        return None

    def olagandisi_denetle(self, t=None):
        """Olağan dışı etkinlik → HER KİPTE anında Durdur(olagandisi). Bundan sonra sayfaya hiçbir işlem yapılmaz. Salt okur."""
        if self.uyari_goruldu: raise Durdur(UYARI_MESAJI, kod="olagandisi")
        t = self.sayfa_metni() if t is None else norm(t)
        if t and any(k in t for k in OLAGANDISI_KELIMELERI):
            self.uyari_goruldu = True
            raise Durdur(UYARI_MESAJI, kod="olagandisi")

    def recaptcha_var(self):
        try:
            return bool(self.oku("""[...document.querySelectorAll('iframe[src*="recaptcha"]')].some(f => {
                const r = f.getBoundingClientRect(); return r.width > 100 && r.height > 100 && getComputedStyle(f).visibility !== 'hidden'; })"""))
        except Exception: return False

    def dogrulama_var_mi(self, t=None, url=True, rc=None):
        if rc is None: rc = self.recaptcha_var()
        if rc: return True
        t = self.sayfa_metni() if t is None else t; u = self.page.url or ""
        return any(k in (t or "") for k in DOGRULAMA_KELIMELERI) or (url and ("accounts.google.com" in u or "/about" in u))

    def kontrol_noktasi(self, giris=False, son=False):
        """Sayfada her işlemden önce (dokun) ve her bekleme diliminde çağrılır. Beklemez, kendiliğinden sürmez: uyarıda 7,
        doğrulama/oturumda 2 ile durdurur. giris=True yalnız --giris içindir: giriş sayfasının adresi doğrulama sayılmaz
        (reCAPTCHA ve doğrulama yazısı yine durdurur). Sayfa okunamazsa işlem yapılmaz (2). Sayfa metni EN SON okunur (dokun'da
        o okumadan sonra yalnız işlemin kendisi gelir)."""
        rc = self.recaptcha_var()
        t = self.sayfa_metni(son=son)
        if t is None:
            raise Durdur("Flow sayfası okunamadı (uyarı denetlenemedi): sayfada işlem yapılmadı. Memmet Chrome'unu kontrol et.", kod="arayuz")
        self.olagandisi_denetle(t)
        if self.dogrulama_var_mi(t, url=not giris, rc=rc):
            raise Durdur("Doğrulama (reCAPTCHA) ya da Google girişi istendi. Memmet beklemeden durdu: Memmet Chrome penceresinde "
                         "kendin çöz, sonra Memmet'i yeniden başlat.", kod="dogrulama")
        if any(k in t for k in KREDI_KELIMELERI): raise Durdur("Flow kredisi bitti.", kod="kredi")

    def son_denetim(self):
        """Sayfa işi bittikten sonra son okuma: son anda beliren uyarı da kilit ve 7 ile kaydedilir."""
        if self.page is not None: self.olagandisi_denetle()

    def kilit_tazele(self):
        if time.time() - self._tazele > FLOW_KILIT_TAZELE_SN: flow_kilidi_tazele(); self._tazele = time.time()

    def bekle_izle(self, sn, giris=False):
        """Uzun bekleme dilimlere bölünür: her dilimden sonra FLOW.kilit tazelenir ve (sayfa açıksa) kontrol noktası salt okunur."""
        kalan = max(0.0, float(sn))
        while True:
            d = min(UYKU_DILIM_SN, kalan)
            if d > 0: uyu(d)
            kalan -= d
            self.kilit_tazele()
            if self.page is not None: self.kontrol_noktasi(giris=giris)
            if kalan <= 0: return

    def bekle_ogeyi(self, secici, sn=45, hata=True):
        """wait_for_selector yerine: her saniye kontrol noktası + öge sayımı (uyarı uzun bekleme içinde kalmaz)."""
        kalan = sn
        while True:
            try:
                if self.page.locator(secici).count() > 0: return True
            except Exception: pass
            if kalan <= 0:
                if hata: raise Durdur(f"Flow arayüzü beklenen sürede gelmedi ({secici}).", kod="arayuz")
                return False
            self.bekle_izle(1); kalan -= 1

    def bekle_adres(self, desen, sn=30):
        kalan = sn
        while not re.search(desen, self.page.url or ""):
            if kalan <= 0: raise Durdur("Flow projesi açılmadı (adres değişmedi).", kod="arayuz")
            self.bekle_izle(1); kalan -= 1

    # ------------------------------------------------------------------ yük sınırı (tempo)
    def tempo_oku(self): return flow_yuk.tempo_oku(HESAP)

    def tempo_bekle(self, tur=None):
        """Bir sonraki izinli zamana kadar bekler (zaman dosyada; Memmet'i yeniden açmak molayı sıfırlamaz). tur verilirse
        flow_yuk'un öteki kuralları da denetlenir: kilit (7), UYARI_GECTI sonrası ilk blok elle, günlük görsel tavanı ve
        görselden videoya bekleme. Saatlerce sürecek bekleme beklenmez: Memmet durur, haber verir."""
        d = flow_yuk.tempo_durumu(self.A["kip"], kok=HESAP, ek=self.tempo_ek()); hedef = d["sonraki_izin"]; kalan = hedef - time.time()
        if kalan > 0:
            if kalan > 60: self.log(f"MOLA / yük sınırı: {int(kalan // 60)} dk {int(kalan % 60)} sn bekleniyor (sayfaya dokunulmuyor)")
            self.bekle_izle(kalan)
        if tur is None: return
        iz = flow_yuk.izinli_mi(tur, self.A["kip"], kok=HESAP, simdi=max(time.time(), hedef), ek=self.tempo_ek())
        if not iz["izinli"]:
            raise Durdur("Flow yük sınırı: " + " ".join(iz["nedenler"]), kod={7: "kilitli", 5: "ortam"}.get(iz["kod"], "yuk"))

    def tempo_ek(self): return {k: self.A[k] for k in TEMPO[self.A["kip"]] if k in self.A}   # MEMMET_AYAR'ın yavaşlattığı değerler

    def gonderim_kaydet(self, tur="video", plan=None):
        T = flow_yuk.gonderim_kaydet(tur, self.A["kip"], film=self.film, plan=plan, kok=HESAP, ek=self.tempo_ek())
        if float(T.get("mola_bitis") or 0) > time.time() and T.get("gonderim_sayaci") and \
                self.A.get("mola_kac_gonderimde") and T["gonderim_sayaci"] % self.A["mola_kac_gonderimde"] == 0:
            self.log(f"{self.A['mola_kac_gonderimde']} gönderim oldu → mola (bitiş {time.strftime('%H:%M', time.localtime(T['mola_bitis']))})")

    def parti_bitti(self):
        """Parti sonu. Mola düştüyse True (mola sonrası proje sayfası yeniden açılır)."""
        mola = flow_yuk.blok_bitti(self.A["kip"], kok=HESAP, ek=self.tempo_ek())
        if mola: self.log("parti molası başladı (bitiş FLOW_TEMPO.json'da)")
        return mola

    def hata_kaydi(self, ad):
        if self.uyari_goruldu: return                      # uyarıdan sonra sayfaya hiç dokunulmaz (salt okuma da yapılmaz)
        base = os.path.join(self.hata_dir, time.strftime("%m%d_%H%M%S_") + ad)
        try: self.page.screenshot(path=base + ".png", timeout=5000)
        except Exception: pass
        try: open(base + ".html", "w", encoding="utf-8").write(self.page.content())
        except Exception: pass
        self.log("hata kaydı:", base)

    def bekle(self, a, b=None):
        self.bekle_izle(random.uniform(a, b if b is not None else a))

    # ------------------------------------------------------------------ giriş ve proje
    def giris_kontrol(self, bekle_giris=False):
        """bekle_giris=True yalnız --giris içindir (sen giriş yaparsın). Üretimde girişsizse beklemez, 2 ile durur.
        Gezinmeden ÖNCE tam kontrol noktası: sekme reCAPTCHA/doğrulama gösteriyorsa gezinmez, 2 ile durur."""
        self.dokun(self.page.goto, FLOW, wait_until="commit", _giris=bekle_giris); self.bekle_izle(4, giris=True)
        self.kontrol_noktasi(giris=True)
        if self.girisli(): return True
        if not bekle_giris:
            raise Durdur("Memmet Chrome'unda Flow girişi yok (oturum düşmüş). FLOW_GIRIS.bat (depo kökü) ile giriş yap, sonra yeniden başlat.", kod="giris")
        self.bildir("Memmet Chrome'unda Google'a giriş yapılmamış. Açılan pencerede Flow'a giriş yap.", acil=True)
        t0 = time.time()
        while not self.girisli():
            self.bekle_izle(10, giris=True)
            if time.time() - t0 > 3600: raise Durdur("Bir saat içinde giriş yapılmadı.", kod="giris")
        return True

    def girisli(self):
        """Girişsiz kullanıcıyı Flow /about tanıtım sayfasına atar; girişliyken hesap düğmesi vardır."""
        u = self.page.url or ""
        if "accounts.google.com" in u or "/about" in u: return False
        try:
            return self.oku("""!!document.querySelector('[aria-label^="Google Hesabı"], [aria-label^="Google Account"]')
                || [...document.querySelectorAll('a[href*="/project/"]')].length > 0 || !!document.querySelector('.ProseMirror')""")
        except Exception: return False

    def projeye_git(self):
        if self.D.get("proje_url"):
            self.dokun(self.page.goto, self.D["proje_url"], wait_until="commit")
        else:
            self.dokun(self.page.goto, FLOW, wait_until="commit"); self.bekle(3)
            self.dokun(self.page.get_by_text("Yeni proje", exact=False).first.click)
            self.bekle_adres(r"/project/", 30); self.bekle(3)
            title = self.page.get_by_role("textbox", name="Düzenlenebilir metin").first
            self.dokun(title.click, click_count=3); self.bekle(0.5)
            self.yaz(self.film[:60]); self.dokun(self.page.keyboard.press, "Enter")
            self.D["proje_url"] = self.page.url.split("?")[0]; self.save()
            self.log("Yeni Flow projesi:", self.film, self.D["proje_url"])
        self.bekle_ogeyi(".ProseMirror", 45); self.bekle(2, 4)
        self.kontrol_noktasi()
        self.yukari()

    def yukari(self):
        try: self.dokun(self.page.evaluate, "(document.getElementById('main-content') || document.scrollingElement).scrollTo(0, 0)")
        except Exception: pass

    def yaz(self, metin):
        """Klavyeyle SABİT gecikmeyle (YAZMA_GECIKMESI_MS) parça parça yazar; her parçadan önce kontrol noktası (dokun)."""
        for i in range(0, len(metin), YAZMA_PARCA):
            self.dokun(self.page.keyboard.type, metin[i:i + YAZMA_PARCA], delay=YAZMA_GECIKMESI_MS)

    # ------------------------------------------------------------------ ayarlar
    def ayar_dugmesi(self): return self.page.get_by_role("button", name="Ayarlar tetikleyicisi").first

    def ayar_yazisi(self): return norm(self.ayar_dugmesi().inner_text())

    def radyo(self, metin):
        """Seçenek yazısı 'simge|Yazı' biçiminde (ör. 'image|Resim'); son parçası eşleşeni tıkla."""
        i = self.oku("""(m) => [...document.querySelectorAll('[role=radio]')]
            .findIndex(r => r.innerText.split('\\n').map(s => s.trim()).includes(m))""", metin)
        if i is None or i < 0: raise Durdur(f"Ayar seçeneği bulunamadı: {metin} (Flow arayüzü değişmiş olabilir)")
        r = self.page.locator("[role=radio]").nth(i)
        if r.get_attribute("aria-checked") != "true": self.dokun(r.click); self.bekle(0.3, 0.7)

    def ayar_menusu_ac(self):
        for _ in range(3):
            self.dokun(self.ayar_dugmesi().click); self.bekle(0.8, 1.2)
            if self.bekle_ogeyi("[role=radio]", 4, hata=False): return
            self.dokun(self.page.keyboard.press, "Escape"); self.bekle(1)
        self.hata_kaydi("ayar_menusu"); raise Durdur("Ayar menüsü açılmadı.")

    def model_sec(self, model):
        """memmet3: açık ayar menüsünde video modelini seçer. Model ayar yazısında görünmediği için hatırlanır. Bulunamazsa seçili modelle sürer."""
        for ac in (self.page.get_by_role("button", name="Model"), self.page.locator("button").filter(has_text="arrow_drop_down")):
            if ac.count() and ac.last.is_visible(): self.dokun(ac.last.click); self.bekle(0.6, 1.0); break
        sec = self.page.get_by_text(model, exact=True)
        if not sec.count(): self.log("UYARI: model bulunamadı, seçili modelle devam:", model); return
        self.dokun(sec.last.click); self.bekle(0.5, 0.9); self._model = model; self.log("Model:", model)

    def mod_ayarla(self, tur, adet=1, model=None):
        """tur: 'gorsel' ya da 'video'; adet: çıktı sayısı (v2 görsel düzeltmesi 2). Yanlışsa düzeltir, sonra yazıdan doğrular.
        memmet3: en boy oranı SAHNELER "en_boy"dan; video modeli (sahne > MEMMET_AYAR)."""
        x = f"x{int(adet)}"; oran = self.plan.get("en_boy", "16:9")
        if oran not in ("16:9", "9:16"): oran = "16:9"
        model = (model or self.A.get("video_model")) if tur == "video" else None
        def dogru():
            y = self.ayar_yazisi()
            if tur == "gorsel": return "nano banana" in y and x in y and "video" not in y
            if model and getattr(self, "_model", None) != model: return False
            return "video" in y and norm(self.A["video_cozunurluk"]) in y and norm(self.A["video_sure"]).replace(".", "") in y.replace(".", "") and x in y
        if dogru(): return
        for deneme in range(2):
            self.ayar_menusu_ac()
            if tur == "gorsel":
                self.radyo("Resim"); self.radyo(oran); self.radyo(x)
            else:
                self.radyo("Video"); self.radyo("Kareler"); self.radyo(oran)
                if model: self.model_sec(model)
                self.radyo(self.A["video_cozunurluk"]); self.radyo(self.A["video_sure"]); self.radyo(x)
            self.dokun(self.page.keyboard.press, "Escape"); self.bekle(0.6, 1.2)
            if dogru(): self.log("Ayar:", self.ayar_yazisi()); return
        self.hata_kaydi("ayar"); raise Durdur(f"Ayar doğrulanamadı ({tur}): {self.ayar_yazisi()}")

    # ------------------------------------------------------------------ yükleme
    def yukle(self, yollar):
        """Dosyaları Flow projesine yükler (adı korunur: mara.jpg, 007.jpg). Daha önce yüklenenleri atlar. Yükleme yüzdeleri beklenirken
        her dilimde uyarı okunur; bekleme bitince (seçiciye geçmeden önce) yeniden tam kontrol noktası."""
        yollar = [p for p in yollar if os.path.basename(p) not in self.D["yuklenen"]]
        for i in range(0, len(yollar), 10):
            grup = yollar[i:i + 10]
            self.yukari()
            self.dokun(self.page.evaluate, """() => { let i = document.getElementById('memmet_yukle'); if (!i) { i = document.createElement('input');
                i.type = 'file'; i.multiple = true; i.id = 'memmet_yukle'; i.style.cssText = 'position:fixed;left:-9999px;top:0';
                document.body.appendChild(i); } }""")
            self.dokun(self.page.set_input_files, "#memmet_yukle", grup)
            self.dokun(self.page.evaluate, """() => { const i = document.getElementById('memmet_yukle'); const dt = new DataTransfer();
                for (const f of i.files) dt.items.add(f); const x = innerWidth / 2, y = innerHeight / 2; const el = document.elementFromPoint(x, y);
                for (const t of ['dragenter', 'dragover', 'drop']) el.dispatchEvent(new DragEvent(t, {bubbles: true, cancelable: true, composed: true, dataTransfer: dt, clientX: x, clientY: y})); }""")
            # liste sanal (görünmeyen karolar sayfada yok), o yüzden karo saymak yerine yükleme yüzdelerinin bitmesini bekle
            sakin, gecen = 0, 0.0
            self.bekle(4); gecen += 4
            while gecen < 180:
                self.bekle(2); gecen += 2
                sakin = sakin + 1 if not self.ilerleme_var() else 0
                if sakin >= 2: break
            else: self.log("UYARI: yükleme beklenenden uzun sürdü", [os.path.basename(p) for p in grup])
            self.kontrol_noktasi()
            self.D["yuklenen"] += [os.path.basename(p) for p in grup]; self.save()
            self.log("yüklendi:", ", ".join(os.path.basename(p) for p in grup))
            self.bekle(*self.A["gonderim_arasi_sn"])
        self.kontrol_noktasi()

    def ilerleme_var(self):
        return self.oku(r"""[...document.querySelectorAll('div.batch-container *')].some(e => e.childElementCount === 0 && /^%\d+$/.test(e.textContent.trim()))""")

    # ------------------------------------------------------------------ istem kutusu
    def kutudaki_icerik(self):
        return self.oku("""() => { const b = document.querySelector('flow-base-prompt-box'); if (!b) return 0;
            let w = b; for (let k = 0; k < 3 && w.parentElement; k++) w = w.parentElement;
            return w.querySelectorAll('img[alt="İçerik öğesi resmi"]').length; }""") or 0

    def secicide_sec(self, dosya):
        """Açık medya seçicisinde dosyayı adıyla bulup isteme ekler."""
        ara = self.page.get_by_placeholder(re.compile("Öğe ara", re.I)).first
        self.dokun(ara.fill, ""); self.dokun(ara.type, dosya, delay=40); self.bekle(1.2, 2)
        opt = self.page.locator("[role=option]").filter(has_text=dosya)
        if opt.count() == 0: raise Durdur(f"Seçicide bulunamadı: {dosya}")
        self.dokun(opt.first.click); self.bekle(0.8, 1.3)
        ekle = self.page.get_by_role("button", name="İsteme ekle")
        if ekle.count() and ekle.first.is_visible() and ekle.first.is_enabled():
            self.dokun(ekle.first.click); self.bekle(0.8, 1.3)
        if self.page.locator("[role=listbox]").count() and self.page.locator("[role=listbox]").first.is_visible():
            self.dokun(self.page.keyboard.press, "Escape"); self.bekle(0.5)

    def referans_ekle(self, dosya):
        once = self.kutudaki_icerik()
        self.dokun(self.page.get_by_role("button", name="İçerik öğelerini istem kutusuna ekle").first.click); self.bekle(1, 1.6)
        self.secicide_sec(dosya)
        if self.kutudaki_icerik() <= once:
            self.hata_kaydi("referans"); raise Durdur(f"Referans istem kutusuna eklenemedi: {dosya}")

    def kare_ekle(self, yuva, dosya):
        self.dokun(self.page.get_by_role("button", name=yuva, exact=True).first.click); self.bekle(1, 1.6)
        self.secicide_sec(dosya)

    def kutuyu_temizle(self):
        """Önceki denemeden kalan referans/kareleri ve yazıyı siler."""
        try:
            x = self.page.locator("flow-base-prompt-box").locator("xpath=../../..").get_by_role("button", name=re.compile("Temizle|Kaldır|close", re.I))
            for _ in range(5):
                if self.kutudaki_icerik() == 0: break
                if x.count(): self.dokun(x.first.click); self.bekle(0.4)
                else: break
        except Exception: pass                       # Durdur BaseException'dır: burada yutulmaz
        pm = self.page.locator(".ProseMirror").first
        self.dokun(pm.click); self.dokun(self.page.keyboard.press, "Control+A"); self.dokun(self.page.keyboard.press, "Delete")

    def gonder_bekle(self, pm, etiket):
        """elle: kullanıcının GÖNDER'e basmasını bekler. Her 2 sn'lik dilimde kontrol noktası ve FLOW.kilit tazeleme (bekle_izle)."""
        t0 = time.time(); hatirlat = t0 + 600
        while norm(pm.inner_text()):
            self.bekle_izle(2)
            if time.time() > hatirlat: self.log(f">> {etiket} hâlâ GÖNDER bekliyor."); hatirlat = time.time() + 600
        return True

    def istem_yaz_gonder(self, metin, etiket=""):
        """İstemi yazar. gece: kendisi gönderir. elle: GÖNDER'e (Oluşturmaya başla) kullanıcının basmasını bekler."""
        pm = self.page.locator(".ProseMirror").first
        self.dokun(pm.click); self.bekle(0.3, 0.6)
        self.yaz(metin)
        self.bekle(0.6, 1.5)
        self.kontrol_noktasi()
        if norm(pm.inner_text())[:40] != norm(metin)[:40]: raise Durdur("İstem kutusuna yazılamadı.", kod="arayuz")
        if self.A["kip"] == "elle":
            self.log(f">> {etiket} HAZIR. Memmet Chrome'unda istemi kontrol et, doğruysa 'Oluşturmaya başla'ya SEN bas.")
            return self.gonder_bekle(pm, etiket)
        self.dokun(self.page.get_by_role("button", name="Oluşturmaya başla").first.click)
        t0 = time.time(); n = 0
        while n < 20:
            self.bekle(1); n += 1
            if not norm(pm.inner_text()): return True
        self.hata_kaydi("gonderim"); self.log("UYARI: GÖNDER'e basıldı ama kutu temizlenmedi: gönderilmiş sayılır (yeniden gönderilmez, toplanır)")
        return None

    # ------------------------------------------------------------------ sonuç takibi
    KART_JS = """(hedef) => {
            const n = s => (s || '').replace(/\\s+/g, ' ').trim().toLowerCase();
            const kutular = [...document.querySelectorAll('div.batch-container')];
            for (const b of kutular) {
                const p = b.querySelector('flow-expandable-prompt'); if (!p) continue;
                const t = n(p.innerText || p.textContent);
                if (!t || !(hedef.startsWith(t.slice(0, 60)) || t.startsWith(hedef.slice(0, 60)))) continue;
                const img = b.querySelector('img[data-media-id]');
                const imgs = [...b.querySelectorAll('img[data-media-id]')].map(i => ({id: i.getAttribute('data-media-id'), url: i.currentSrc || i.src}));
                const vid = [...b.querySelectorAll('video')].map(v => v.currentSrc || v.src).find(s => /flow-content\\.google\\/video\\//.test(s));
                const yuzde = [...b.querySelectorAll('*')].some(e => e.childElementCount === 0 && /^%\\d+$/.test(e.textContent.trim()));
                // hata metni: istem ögesinin DIŞINDAKİ yazılar (istemdeki "failed/policy" kelimeleri kartı reddedilmiş saydırmaz)
                const w = document.createTreeWalker(b, NodeFilter.SHOW_TEXT); const dis = [];
                for (let x = w.nextNode(); x; x = w.nextNode()) { const e = x.parentElement; if (!e || !e.closest('flow-expandable-prompt')) dis.push(x.nodeValue); }
                // açık hata ögesi: role=alert / aria-live=assertive / hata simgesi ya da hata sınıfı (istem dışında)
                const hoge = [...b.querySelectorAll('[role=alert], [aria-live=assertive], [class*=error i], [class*=hata i], [data-error]')]
                    .some(e => !e.closest('flow-expandable-prompt'))
                    || [...b.querySelectorAll('mat-icon, i, span[class*=icon i], .material-icons, .material-symbols-outlined')]
                    .some(e => !e.closest('flow-expandable-prompt') && /^(error|error_outline|warning|report|block|gpp_bad)$/.test(n(e.textContent)));
                return {var: true, gorsel_id: img ? img.getAttribute('data-media-id') : null, gorsel_url: img ? (img.currentSrc || img.src) : null,
                        gorseller: imgs,
                        video_url: vid || null, video_kutusu: !!b.querySelector('flow-video-tile'), yuzde,
                        metin: n(b.innerText).slice(0, 400), hata_metni: n(dis.join(' ')).slice(0, 400), hata_ogesi: hoge, sira: kutular.indexOf(b)};
            }
            return {var: false};
        }"""

    def kutu_bul(self, metin):
        """İstem metniyle eşleşen üretim kutusunun durumunu döndürür. metin: bütün kart (uyarı denetimi için); hata_metni: istem dışı."""
        return self.oku(self.KART_JS, norm(metin)) or {"var": False}

    @staticmethod
    def red_mi(r, kelimeler):
        """Kart reddedilmiş/hatalı mı: kart var, yüzde yok, sonuç yok, AÇIK hata ögesi var ve istem DIŞINDAKİ yazıda kelime geçer.
        Emin olunamayan kart reddedilmiş sayılmaz (zaman aşımına düşer → yeniden gönderilmez, toplanır)."""
        return bool(r.get("var") and not r.get("yuzde") and not r.get("gorsel_url") and not r.get("video_kutusu") and r.get("hata_ogesi")
                    and any(k in (r.get("hata_metni") or "") for k in kelimeler))

    def video_adresi(self, metin):
        """Video kutusunun üstüne gelip <video> adresini yükletir (kaydırma, üstüne gelme ve fare dokun() ile)."""
        idx = self.kutu_bul(metin).get("sira")
        if idx is None: return None
        tile = self.page.locator("div.batch-container").nth(idx).locator("flow-video-tile").first
        try: self.dokun(tile.scroll_into_view_if_needed, timeout=5000); self.dokun(tile.hover, timeout=5000)
        except Exception: return None                # Durdur BaseException'dır: burada yutulmaz
        for _ in range(10):
            self.bekle(0.6)
            r = self.kutu_bul(metin)
            if r.get("var"): self.olagandisi_denetle(r.get("metin", ""))
            if r.get("video_url"): self.dokun(self.page.mouse.move, 5, 5); return r["video_url"]
        return None

    def indir(self, url, hedef):
        tmp = hedef + ".part"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": FLOW})
            with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f: shutil.copyfileobj(r, f)
        except Exception as e:   # yedek yol: dosyayı sayfanın içinden al (salt okuma: fetch)
            self.log("doğrudan indirme olmadı, sayfa içinden alınıyor:", str(e)[:60])
            import base64
            self.olagandisi_denetle()
            b64 = self.oku("""async (u) => { const r = await fetch(u); const b = await r.blob();
                return await new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result.split(',')[1]); fr.readAsDataURL(b); }); }""", url)
            open(tmp, "wb").write(base64.b64decode(b64))
        if os.path.getsize(tmp) < 10_000: os.remove(tmp); raise RuntimeError("indirilen dosya çok küçük")
        os.replace(tmp, hedef)

    # ------------------------------------------------------------------ KONTROL ile köprü
    def kontrol_isle(self, n, tur, kaynak):
        try:
            import kontrol
            f = kontrol.Film(self.root); s = f.sc(n)
            if tur == "gorsel": s.update(gorsel=kaynak, gorsel_emin=True, gorsel_skor=None, gorsel_kaynak="memmet")
            else: s.update(video=kaynak, video_emin=True, video_skor=None, video_kaynak="memmet")
            f.save()
        except Exception as e: self.log("KONTROL güncellenemedi:", str(e)[:100])

    # ------------------------------------------------------------------ üretim döngüsü (v1: yalnız görsel)
    def sahneler(self, parti=None):
        out = []
        for s in self.plan["sahneler"]:
            if s.get("motor", "flow") != "flow": continue
            if parti is not None and s.get("parti") != parti: continue
            if self.args.get("sahne") and s["no"] not in self.args["sahne"]: continue
            out.append(s)
        return out

    def istemler(self, s, tur):
        ana = s["gorsel_istem"] if tur == "gorsel" else s["hareket_istem"]
        yedek = s.get("gorsel_istem_yedek" if tur == "gorsel" else "hareket_istem_yedek")
        return [ana, ana] + ([yedek] if yedek else [])          # Flow'un AÇIK hata verdiği görselde 2 deneme, sonra yedek

    def v1_video_yok(self):
        raise Durdur("v1 (eski SAHNELER) filmde video gönderimi kapalı: animatik imzası ve bütçe noktası yok. Film v2'ye taşınmalı "
                     "(film.py); v1'de yalnız görsel üretilir. Hiçbir şey gönderilmedi.", kod="surum")

    def v1_topla(self, tur, sahneler, hedef_dir, ext):
        """Zaman aşımına uğramış v1 işleri yeniden GÖNDERİLMEZ: önce sayfada aranır (salt okuma); hazırsa indirilir."""
        for s in sahneler:
            st = self.sc(s["no"])
            if st.get(tur + "_durum") != "zaman_asimi": continue
            r = self.kutu_bul(st.get(tur + "_istem") or "")
            if r.get("var"): self.olagandisi_denetle(r.get("metin", ""))
            if r.get("var") and r.get("gorsel_url") and not r.get("yuzde"):
                try:
                    self.indir(r["gorsel_url"], os.path.join(hedef_dir, f"{s['no']:03d}.{ext}")); st[tur + "_durum"] = "tamam"; self.save()
                    self.log(f"{s['no']:03d} {tur}: zaman aşımı sonrası toplandı (yeniden gönderilmedi)")
                except Exception as e: self.log(f"{s['no']:03d} toplanamadı: {str(e)[:80]}")
            else: self.log(f"{s['no']:03d} {tur}: zaman aşımı → yeniden gönderilmez; Flow'da elle bak (sürüyor ya da kayıp)")

    def asama(self, tur, sahneler):
        if tur != "gorsel": self.v1_video_yok()
        hedef_dir = self.sg; ext = "jpg"
        self.v1_topla(tur, sahneler, hedef_dir, ext)
        isler = [s for s in sahneler if not os.path.exists(os.path.join(hedef_dir, f"{s['no']:03d}.{ext}"))
                 and self.sc(s["no"]).get(tur + "_durum") not in ("reddedildi", "zaman_asimi")]
        if not isler: self.log(f"{tur}: yapılacak sahne yok"); return
        self.log(f"=== {tur.upper()} aşaması: {len(isler)} sahne ({', '.join(str(s['no']) for s in isler)})")
        adet = self.A.get("gorsel_adet", 1)
        self.mod_ayarla(tur, adet)
        refs = {r for s in isler for r in s.get("referans", [])}
        if self.A["kip"] != "elle":   # memmet3 (19.10 kullanıcı): elle kipte refler topluca değil, sahnesi gelince tek tek yüklenir
            self.yukle([os.path.join(self.root, self.plan["karakterler"][r]["ref"]) for r in sorted(refs)])
        kuyruk = list(isler); bekleyen = {}       # sahne no -> {istem, gonderim, deneme}
        zaman_asimi = self.A["gorsel_zaman_asimi_sn"]
        while kuyruk or bekleyen:
            self.kontrol_noktasi(); self.kilit_tazele()
            # yeni gönderim
            if kuyruk and len(bekleyen) < self.A["ayni_anda"]:
                s = kuyruk.pop(0); st = self.sc(s["no"]); deneme = st.get(tur + "_deneme", 0)
                ist = self.istemler(s, tur)
                if deneme >= len(ist):
                    st[tur + "_durum"] = "reddedildi"; self.save(); self.log(f"{s['no']:03d} {tur}: bütün denemeler bitti → reddedildi")
                    continue
                metin = ist[deneme]
                self.tempo_bekle(tur); self.kontrol_noktasi()
                try:
                    self.mod_ayarla(tur, adet); self.kutuyu_temizle()
                    for r in s.get("referans", []):
                        ref = self.plan["karakterler"][r]["ref"]
                        if os.path.basename(ref) not in self.D["yuklenen"]: self.yukle([os.path.join(self.root, ref)])
                        self.referans_ekle(os.path.basename(ref))
                    ok = self.istem_yaz_gonder(metin, f"{s['no']:03d} {tur}")
                except Exception as e:
                    self.hata_kaydi(f"{s['no']:03d}_{tur}"); self.log(f"{s['no']:03d} {tur}: gönderim hatası: {str(e)[:150]}")
                    ok = False
                st[tur + "_deneme"] = deneme + 1; st[tur + "_istem"] = metin; self.save()
                if ok is not False: self.gonderim_kaydet(tur, s["no"])     # None: basıldı, belirsiz → gönderilmiş sayılır
                if ok is not False:
                    bekleyen[s["no"]] = {"istem": metin, "t": time.time(), "s": s}
                    self.log(f"{s['no']:03d} {tur}: gönderildi (deneme {deneme + 1}{', yedek istem' if deneme >= 2 else ''})")
                else:
                    kuyruk.insert(0, s); self.projeye_git()
                continue
            # sonuçları kontrol et
            self.bekle(4, 7)
            self.kontrol_noktasi()
            for n in list(bekleyen):
                b = bekleyen[n]; s = b["s"]; r = self.kutu_bul(b["istem"]); gecen = time.time() - b["t"]
                if r.get("var"): self.olagandisi_denetle(r.get("metin", ""))
                hedef = os.path.join(hedef_dir, f"{n:03d}.{ext}")
                if r.get("var") and r.get("gorsel_url") and not r.get("yuzde"):
                    try:
                        self.indir(r["gorsel_url"], hedef); self.kontrol_isle(n, tur, f"memmet:{r['gorsel_id']}")
                        ekler = [g["url"] for g in (r.get("gorseller") or []) if g.get("url") and g["url"] != r["gorsel_url"]]
                        for k, u in enumerate(ekler[:adet - 1]):        # memmet3 x2: ek aday NNN_b.jpg (indirme; sayfaya dokunmaz)
                            try: self.indir(u, hedef[:-4] + "_" + "bcd"[k] + ".jpg")
                            except Exception as e: self.log(f"{n:03d} ek aday indirilemedi: {str(e)[:60]}")
                        self.sc(n)[tur + "_durum"] = "tamam"; self.save(); self.log(f"{n:03d} görsel: KAYDEDİLDİ ({int(gecen)} sn)")
                        del bekleyen[n]
                    except Exception as e: self.log(f"{n:03d} görsel indirilemedi, tekrar denenecek: {str(e)[:80]}")
                    continue
                if self.red_mi(r, HATA_KELIMELERI):        # Flow AÇIK hata verdi: görsel (0 kredi) sıradaki istemle yeniden
                    self.log(f"{n:03d} {tur}: Flow reddetti/hata → sıradaki istem. Flow'un yazısı: {r.get('hata_metni', '')[:160]}")
                    del bekleyen[n]; kuyruk.append(s)
                elif gecen > zaman_asimi:                  # zaman aşımı: yeniden gönderim YOK, sayfa yenilenmez; sonra toplanır
                    self.sc(n)[tur + "_durum"] = "zaman_asimi"; self.save(); del bekleyen[n]
                    self.log(f"{n:03d} {tur}: zaman aşımı → yeniden gönderilmez (sonraki açılışta önce toplanır)")

    # ------------------------------------------------------------------ v2: hesap kimliği ve bakiye (salt okuma)
    def hesap_denetle(self):
        """Flow'da görünen hesabın yalnız sha1'i (D-03). Son uyarıdan sonra hesap değiştiyse kilit → 7. E-posta yazılmaz, loglanmaz."""
        try: etiket = self.oku("""(() => { const b = document.querySelector('[aria-label^="Google Hesabı"], [aria-label^="Google Account"]');
            return b ? (b.getAttribute('aria-label') || '') : ''; })()""")
        except Exception: etiket = ""
        m = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", etiket or "")
        if not m:
            T = flow_yuk.tempo_oku(HESAP)
            if flow_yuk.uyarilar_oku(HESAP) or T.get("son_uyari") or T.get("uyari_gecti"):
                raise Durdur("Flow hesabı sayfadan okunamadı ve bu hesapta uyarı geçmişi var: hesabın asıl hesap olduğu doğrulanamadan "
                             "gönderilmez. Memmet Chrome'unda Flow'a asıl hesabınla girili olduğunu kontrol et.", kod="hesap")
            self.log("Flow hesabı sayfadan okunamadı (hesap kimliği ÖLÇÜLEMEDİ; uyarı geçmişi yok, devam; kilit kuralı FLOW_KILIDI ile sürer)")
            self.hesap = None; return None
        r = flow_yuk.hesap_gozlem(eposta=m.group(0), kok=HESAP); self.hesap = r["kimlik"][:8]
        if r.get("bilgi"): self.log(r["bilgi"])
        if r.get("kilit"):
            raise Durdur("Flow hesabı değişti (son uyarıdan sonra). Başka Google/Flow hesabıyla devam edilmez; asıl hesaba dön.", kod="kilitli")
        return self.hesap

    def bakiye_oku(self):
        """--bakiye: sayfa metninden kredi bakiyesi (tıklama ve gönderim yok). Bulunamazsa ÖLÇÜLEMEDİ (null)."""
        self.kontrol_noktasi()
        t = self.sayfa_metni() or ""
        m = re.search(r"(\d[\d.,]*)\s*(?:ai\s*)?(?:kredi|credits?)\b", t)
        b = int(re.sub(r"[.,]", "", m.group(1))) if m else None
        _atomik(os.path.join(HESAP, "FLOW_BAKIYE.json"), {"_surum": 1, "bakiye": b, "olculemedi": b is None, "kaynak": "flow_sayfa_metni",
                                                           "hesap": self.hesap, "zaman": time.strftime("%Y-%m-%d %H:%M:%S")})
        self.log("Flow bakiyesi:", b if b is not None else "ÖLÇÜLEMEDİ (sayfada kredi yazısı bulunamadı)")
        return b

    # ------------------------------------------------------------------ v2: blok (BLOK_PLANI.json)
    def dur_var(self): return os.path.exists(os.path.join(self.root, "DUR"))

    def blok_dogrula(self):
        """Chrome açılmadan önce: blok, önizleme imzası (BUT2), animatik imzası, sağlayıcı. Sayfaya dokunmaz."""
        import blok_plani
        try: BP, b = blok_plani.blok_bul(self.root, self.args["blok"])
        except ValueError as e: raise Durdur(str(e), kod="imza")
        imza = blok_plani.onizleme_imza(self.root)
        if not imza: raise Durdur("Kesin bütçe yok (URETIM_ONIZLEME.json taslak): önce kredi.py but2. Hiçbir şey gönderilmedi.", kod="imza")
        if self.args.get("onizleme") != imza or BP.get("onizleme_imza") != imza:
            raise Durdur("Önizleme imzası tutmuyor (bütçe ya da plan değişti): blok_plani.py yeniden koşmalı. Hiçbir şey gönderilmedi.", kod="imza")
        if not blok_plani.animatik_onayli(self.root):
            raise Durdur("Animatik imzası yok (FILM_DURUM animatik: ONAYLI değil): video kredisi harcanmaz.", kod="imza")
        if (b.get("saglayici") or "flow") != "flow":
            raise Durdur(f"Blok {b['id']} Flow'a değil ({b.get('saglayici')}): Memmet göndermez.", kod="ortam")
        sag = str((ortak.json_oku(os.path.join(self.root, "HAZIRLIK.json"), {}) or {}).get("saglayici") or "").lower()
        if sag in ("sahte", "kaset"):
            raise Durdur(f"Bu film '{sag}' deneme filmi (HAZIRLIK.json): Flow'a gerçek gönderim yapılmaz.", kod="ortam")
        ok, neden, _ = animatik_imza.dogrula(self.root)      # önbelleğe güvenilmez: imza bütün dosyalarla yeniden doğrulanır
        if not ok: raise Durdur(f"Animatik imzası geçersiz ({neden}): video kredisi harcanmaz. Hiçbir şey gönderilmedi.", kod="imza")
        if len(b.get("planlar") or []) > blok_plani.BLOK_MAX:
            raise Durdur(f"Blok {b['id']} {blok_plani.BLOK_MAX} plandan büyük: blok_plani.py yeniden koşmalı.", kod="imza")
        self.blok, self.blok_id = b, str(b["id"]); self.blok_nolar = {int(n) for n in b.get("planlar") or []}
        self.planlar = {int(p["no"]): p for p in self.plan.get("sahneler") or [] if isinstance(p.get("no"), (int, float))}
        return b

    def atla(self, no, neden):
        self.ozet["atlanan"].append({"plan": no, "neden": neden}); self.log(f"{no:03d}: atlandı ({neden})"); return None

    def kredi_birim(self, tur):
        if tur == "gorsel": return 0                          # Flow görsel düzeltmesi 0 kr (günlük tavanla sınırlı)
        try:
            import esikler; return int(esikler.yukle().get("kredi_klip_720p") or 12)
        except Exception: return 12

    def is_hazirla(self, no, tur, yedek=False):
        """Gönderilecek işin bütün bilgisi; plan şu an uygun değilse None (neden ozet.atlanan'da)."""
        import blok_plani
        p = self.planlar.get(no)
        if p is None: return self.atla(no, "SAHNELER'de yok")
        ayr = (self.blok.get("ayrinti") or {}).get(str(no)) or {}
        uygun, neden = blok_plani.uygun_mu(self.root, p, self.planlar, tur=tur, blok_nolar=self.blok_nolar, isler=self.D["isler"],
                                           yeniden=bool(ayr.get("madde")))
        if not uygun: return self.atla(no, neden)
        if tur == "video":
            hazir, neden = self.video_hazir(no, p)
            if not hazir: return self.atla(no, neden)
        alan = "gorsel_istem" if tur == "gorsel" else "hareket_istem"
        ana = ayr.get("istem") or p.get(alan); yd = p.get(alan + "_yedek")
        istem = yd if yedek else ana
        if not istem: return self.atla(no, "istem yok" if not yedek else "yedek istem yok")
        dosyalar = blok_plani.gonderim_gorselleri(self.root, p, self.plan, tur, ayr)
        if dosyalar is None: return self.atla(no, "başlangıç/bitiş görseli yok")
        u = p.get("uretim") or {}
        deneme = blok_plani.deneme_sayisi(self.root, no, tur) + 1
        model = u.get("model") or "omni-1.1-flash"; coz = self.A["video_cozunurluk"]
        ozt = hashlib.sha1(json.dumps([no, tur, istem, [d["sha"] for d in dosyalar], model, coz, deneme],
                                      ensure_ascii=False).encode("utf-8")).hexdigest()[:6]
        kim = f"{'G' if tur == 'gorsel' else 'V'}-{no}-d{deneme}-{ozt}"
        return {"plan": no, "tur": tur, "istem": istem, "yedek": bool(yedek), "yedek_var": bool(yd) and not yedek, "dosyalar": dosyalar,
                "deneme": deneme, "is": kim, "madde": ayr.get("madde") or kim, "dilim": ayr.get("dilim") or "ana",
                "kredi": self.kredi_birim(tur), "model": model, "cozunurluk": coz}

    def video_hazir(self, no, p):
        """Her video gönderiminden önce ikinci denetim: kare_denetim.video_hazir (G1 GEÇ ya da son_kare zincirinde uretim.zincir.g1z GEÇ +
        SIRALI_GORSEL SHA1'i kayıtla aynı, ≥ 8 haneli önek kabul; D-15, §1.5 kural 6). Denetlenemezse gönderilmez (kapalı başarısız)."""
        try: ok, neden = kare_denetim.video_hazir(self.root, no)
        except Exception as e:
            return False, f"video_hazir denetlenemedi ({str(e)[:80]}): gönderilmedi"
        return (True, "") if ok else (False, f"kare videoya hazır değil: {neden}")

    def kredi_once(self, j):
        """Bütçe noktası (BUTK) + kredi defterine gönderim satırı: GÖNDERİMDEN ÖNCE. Onay yoksa 5 (yeni gönderim yok)."""
        import kredi
        try: r, kod = kredi.butk(self.root, j["madde"], j["kredi"], birim="flow", dilim=j["dilim"], saglayici="flow", plan=j["plan"])
        except kredi.Girdi as e: raise Durdur(f"Bütçe noktası koşamadı: {e}", kod="butce")
        if kod != 0:
            neden = r.get("neden") or (r.get("hatalar") or [{}])[0].get("esik")
            raise Durdur(f"Bütçe noktası (BUTK) {j['plan']:03d} için onay vermedi: {neden}. Yeni gönderim yok.", kod="butce")
        kredi.defter_ekle(self.root, "gonderim", j["kredi"], birim="flow", dilim=j["dilim"], madde=j["madde"], plan=j["plan"],
                          saglayici="flow", is_kimligi=j["is"], tur=j["tur"], deneme=j["deneme"], model=j["model"],
                          cozunurluk=j["cozunurluk"], blok=self.blok_id, yedek_istem=j["yedek"] or None)
        self.D["isler"][j["is"]] = {"plan": j["plan"], "tur": j["tur"], "istem": j["istem"], "durum": "gonderildi", "blok": self.blok_id,
                                    "deneme": j["deneme"], "yedek": j["yedek"], "zaman": time.strftime("%Y-%m-%d %H:%M:%S")}
        self.save()

    def kredi_iade(self, j, neden):
        import kredi
        kredi.defter_ekle(self.root, "iade", j["kredi"], birim="flow", dilim=j["dilim"], madde=j["madde"], plan=j["plan"],
                          saglayici="flow", is_kimligi=j["is"], neden=neden)
        self.D["isler"][j["is"]]["durum"] = "iade"; self.save()

    def yukle_adli(self, dosyalar):
        """Görselleri sha'lı adla (NNN_<sha8>.jpg) yükler: aynı adla eski bir görsel Flow'da kalmışsa yanlış kare seçilmesin."""
        yollar = []
        for d in dosyalar:
            hedef = os.path.join(self.gecici, d["ad"])
            if not os.path.exists(hedef): shutil.copyfile(d["yol"], hedef)
            yollar.append(hedef)
        self.yukle(yollar)

    def eskiye_tasi(self, yol):
        """Kalıcı silme yok: var olan dosya <film>/_ESKI/'ye taşınır."""
        if not os.path.exists(yol): return
        rel = os.path.relpath(yol, self.root); hedef = os.path.join(self.root, "_ESKI", time.strftime("%Y%m%d_%H%M%S_") + rel.replace(os.sep, "_"))
        os.makedirs(os.path.dirname(hedef), exist_ok=True); shutil.move(yol, hedef)

    def kunye_yaz(self, b, dosyalar, medya):
        j = b["j"]; no = j["plan"]; p = self.planlar.get(no) or {}; u = p.get("uretim") or {}
        k = {"_surum": 1, "plan": no, "tur": j["tur"], "dosyalar": dosyalar, "baslangic": j["dosyalar"][0]["sha"] if j["dosyalar"] else None,
             "bitis": next((d["sha"] for d in j["dosyalar"] if d["yuva"] == "Bitir"), None),
             "istem_sha": hashlib.sha1(j["istem"].encode("utf-8")).hexdigest()[:12], "yedek_istem": j["yedek"], "saglayici": "flow",
             "model": j["model"], "cozunurluk": j["cozunurluk"], "istem_bicimi": u.get("istem_bicimi"), "deneme": j["deneme"],
             "is": j["is"], "flow_medya_id": medya, "plan_imza": __import__("blok_plani").plan_imza(p) if p else None,
             "blok": self.blok_id, "mod": self.A["kip"],
             "zaman": time.strftime("%Y-%m-%d %H:%M:%S"), "kapilar": {}}
        if j["tur"] == "video":
            yol = os.path.join(self.root, "KUNYE", f"{no:03d}.json"); self.eskiye_tasi(yol); _atomik(yol, k)

    def indir_v2(self, b, r):
        """Sonuç hazırsa indirir (True). Video: SIRALI_VIDEO/NNN.mp4 (eski dosya _ESKI/'ye). Görsel: _ADAYLAR/NNN_flow_<is>_<i>.jpg."""
        j = b["j"]; no = j["plan"]
        if j["tur"] == "video":
            url = r.get("video_url") or self.video_adresi(b["istem"])
            if not url: return False
            gecici = os.path.join(self.gecici, f"{no:03d}_{j['is']}.mp4"); self.indir(url, gecici)
            hedef = os.path.join(self.sv, f"{no:03d}.mp4"); self.eskiye_tasi(hedef); os.replace(gecici, hedef)
            medya = (re.search(r"video/([0-9a-f-]{36})", url) or [None, None])[1]
            self.kunye_yaz(b, [os.path.relpath(hedef, self.root).replace(os.sep, "/")], medya)
        else:
            gs = [g for g in (r.get("gorseller") or []) if g.get("url")] or ([{"id": r.get("gorsel_id"), "url": r["gorsel_url"]}] if r.get("gorsel_url") else [])
            if not gs: return False
            klasor = os.path.join(self.sg, "_ADAYLAR"); os.makedirs(klasor, exist_ok=True); cikan = []
            for i, g in enumerate(gs[:2]):
                hedef = os.path.join(klasor, f"{no:03d}_flow_{j['is']}_{'ab'[i]}.jpg"); self.indir(g["url"], hedef)
                cikan.append(os.path.relpath(hedef, self.root).replace(os.sep, "/"))
            medya = ",".join(str(g.get("id")) for g in gs[:2])
        self.D["isler"][j["is"]].update(durum="indirildi", indirme=time.strftime("%Y-%m-%d %H:%M:%S"), medya=medya); self.save()
        self.ozet["indirilen"].append(no); self.log(f"{no:03d} {j['tur']}: KAYDEDİLDİ ({int(time.time() - b['t'])} sn)")
        return True

    def blok_asama(self):
        """Bir blok: her gönderimden önce kontrol noktası, DUR, tempo/yük (FLOW_TEMPO), uygunluk, BUTK + kredi satırı.
        Uyarı her an Durdur(olagandisi) ile çıkar (sayfada başka işlem yok). Yeniden deneme yalnız filtre reddinde yedek istemle, bir kez."""
        tur = self.blok.get("tur") or "video"; adet = 2 if tur == "gorsel" else 1
        self.ozet = {"blok": self.blok_id, "tur": tur, "gonderilen": [], "indirilen": [], "bekleyen": [], "reddedilen": [], "hata": [],
                     "zaman_asimi": [], "atlanan": [], "dur": False}
        nolar = [int(n) for n in self.blok.get("planlar") or []]
        self.log(f"=== BLOK {self.blok_id} ({tur}, kip {self.A['kip']}): {len(nolar)} plan ({', '.join(str(n) for n in nolar)})")
        self.mod_ayarla(tur, adet)
        import blok_plani
        on = [blok_plani.gonderim_gorselleri(self.root, self.planlar[n], self.plan, tur, (self.blok.get("ayrinti") or {}).get(str(n)) or {})
              for n in nolar if n in self.planlar]
        self.yukle_adli([d for ds in on if ds for d in ds])
        kuyruk = [(n, False) for n in nolar]; bekleyen = {}
        zaman_asimi = self.A["gorsel_zaman_asimi_sn" if tur == "gorsel" else "video_zaman_asimi_sn"]
        while kuyruk or bekleyen:
            self.kontrol_noktasi(); self.kilit_tazele()
            if kuyruk and self.dur_var():
                self.log("DUR dosyası var: yeni gönderim yok; elimdeki sonuçlar bekleniyor.")
                for n, _ in kuyruk: self.ozet["atlanan"].append({"plan": n, "neden": "DUR"})
                kuyruk = []; self.ozet["dur"] = True
            if kuyruk and len(bekleyen) < self.A["ayni_anda"]:
                no, yedek = kuyruk.pop(0)
                j = self.is_hazirla(no, tur, yedek)
                if j is None: continue
                self.tempo_bekle(tur); self.kontrol_noktasi()
                if self.dur_var(): kuyruk.insert(0, (no, yedek)); continue          # beklerken DUR geldiyse gönderme
                self.kredi_once(j)
                ok = False
                try:
                    self.mod_ayarla(tur, adet); self.kutuyu_temizle()
                    self.yukle_adli(j["dosyalar"])
                    for d in j["dosyalar"]:
                        if d["yuva"] == "Referans": self.referans_ekle(d["ad"])
                        else: self.kare_ekle(d["yuva"], d["ad"])
                    ok = self.istem_yaz_gonder(j["istem"], f"{no:03d} {tur}{' (yedek istem)' if yedek else ''}")
                except Exception as e:                    # Durdur BaseException'dır: buradan geçer, yutulmaz
                    self.hata_kaydi(f"{no:03d}_{tur}"); self.log(f"{no:03d} {tur}: gönderim hatası: {str(e)[:150]}")
                if ok is not False:                       # None: GÖNDER'e basıldı ama kutu boşalmadı → gönderilmiş sayılır (iade yok, toplanır)
                    self.gonderim_kaydet(tur, no); bekleyen[no] = {"istem": j["istem"], "t": time.time(), "j": j}
                    self.ozet["gonderilen"].append(no); self.log(f"{no:03d} {tur}: gönderildi ({j['is']})")
                else:      # gönderilmedi: kredi satırı iade edilir, aynı blokta yeniden denenmez (blok_plani sonra yeniden koyar)
                    self.kredi_iade(j, "gönderilemedi"); self.ozet["hata"].append({"plan": no, "neden": "gönderilemedi"})
                    self.projeye_git()
                continue
            self.bekle(4, 7)
            self.kontrol_noktasi()
            for no in list(bekleyen):
                b = bekleyen[no]; j = b["j"]; r = self.kutu_bul(b["istem"]); gecen = time.time() - b["t"]
                if r.get("var"): self.olagandisi_denetle(r.get("metin", ""))
                hazir = r.get("var") and not r.get("yuzde") and (r.get("video_kutusu") if tur == "video" else r.get("gorsel_url"))
                if hazir:
                    try:
                        if self.indir_v2(b, r): del bekleyen[no]
                    except Exception as e: self.log(f"{no:03d} indirilemedi, sonra yeniden okunacak: {str(e)[:80]}")
                    if no not in bekleyen or gecen <= zaman_asimi: continue
                metin = r.get("hata_metni") or ""          # istem DIŞINDAKİ yazı; açık hata ögesi şart (red_mi)
                if self.red_mi(r, FILTRE_KELIMELERI):
                    del bekleyen[no]; self.D["isler"][j["is"]]["durum"] = "filtre_red"; self.save()
                    if j["yedek_var"]:
                        self.log(f"{no:03d}: filtre reddi → derlenmiş yedek istem BİR kez"); kuyruk.insert(0, (no, True))
                    else:
                        self.log(f"{no:03d}: filtre reddi{' (yedek de)' if j['yedek'] else ''} → yonetmen·onarim; yeniden gönderilmez")
                        self.ozet["reddedilen"].append({"plan": no, "neden": "filtre_red", "yedek_denendi": j["yedek"], "flow": metin[:160]})
                elif self.red_mi(r, HATA_KELIMELERI):
                    del bekleyen[no]; self.D["isler"][j["is"]]["durum"] = "hata"; self.save()
                    self.ozet["hata"].append({"plan": no, "neden": "flow_hata", "flow": metin[:160]})
                    self.log(f"{no:03d}: Flow hata verdi → bu blokta yeniden gönderilmez (blok_plani karar verir)")
                elif gecen > zaman_asimi:     # zaman aşımı: yeniden gönderim YOK; önce toplanır (memmet_topla.py)
                    del bekleyen[no]; self.D["isler"][j["is"]]["durum"] = "zaman_asimi"; self.save()
                    self.ozet["zaman_asimi"].append(no); self.log(f"{no:03d}: zaman aşımı → toplanacak (memmet_topla), yeniden gönderilmez")
        return self.ozet

    def blok_bitir(self):
        """Blok sonu (sayfa işi bitti): FLOW raporu, blok işareti, blok molası (FLOW_TEMPO), V1 + SC1 indirilenlere."""
        import blok_plani
        o = self.ozet; o["bekleyen"] = list(o["zaman_asimi"])
        try: blok_plani.flow_raporu(self.root, self.blok_id, o, self.blok.get("planlar") or [], gorev=os.environ.get("YZ_FILM_GOREV"))
        except Exception as e: self.log("FLOW raporu yazılamadı:", str(e)[:120])
        if not o["zaman_asimi"] and not o["dur"]: blok_plani.bitti_isaretle(self.root, self.blok_id, o)
        if self.parti_bitti(): self.log("blok molası (bitiş FLOW_TEMPO.json'da); sonraki blok o zamandan önce gönderilmez")
        if o["indirilen"] and o["tur"] == "video": self.blok_denetimleri(o["indirilen"])
        self.bildir(f"Blok {self.blok_id} bitti: {len(o['indirilen'])} indirildi, {len(o['reddedilen'])} red, {len(o['zaman_asimi'])} toplanacak.")
        return o

    def blok_denetimleri(self, nolar):
        """Her indirmede V1 (kalite_denetim --klip) ve SC1 (ses_donustur --hizala). Sayfaya dokunmaz; hatası Memmet'i durdurmaz."""
        for ad, modul, fonk in (("V1", "kalite_denetim", "klip_denetle"), ("SC1", "ses_donustur", "hizala")):
            try:
                m = __import__(modul); getattr(m, fonk)(self.root, nolar, blok=self.blok_id)
            except Exception as e: self.log(f"{ad} koşamadı (sonra film.py yeniden koşar): {str(e)[:120]}")

    def blok_calis(self):
        self.on_kosullar(); self.blok_dogrula()
        flow_kilidi_al(self.film)
        try: ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
        except Exception: pass
        self.chrome_ac(); self.giris_kontrol(); self.hesap_denetle(); self.projeye_git()
        self.bildir(f"Blok {self.blok_id} başladı ({self.A['kip']}).")
        self.blok_asama()
        o = self.blok_bitir()
        self.son_denetim()
        if o["dur"]: raise Durdur(f"DUR dosyası: blok {self.blok_id} yarıda bırakıldı (yeni gönderim yok). DEVAM.bat ile sürer.", kod="dur")
        if o["zaman_asimi"]:
            raise Durdur(f"{len(o['zaman_asimi'])} plan zaman aşımına uğradı: yeniden gönderilmedi, önce toplanacak (VIDEO_TOPLA.bat / "
                         "memmet_topla.py).", kod="topla")
        return o

    def on_kosullar(self):
        """Chrome açılmadan önce: kilit ve izin. Sayfaya dokunmaz."""
        k = flow_yuk.kilit_durumu(kok=HESAP)
        if k["kilitli"]:
            raise Durdur(f"Flow kilidi var ({k['neden']}; en erken {k['en_erken_metin']}). Memmet açılmadı. "
                         "GÖNDER'e basma; Claude'a haber ver.", kod="kilitli")
        if self.A["kip"] == "gece" and not gece_izni():
            raise Durdur("Gece kipi kapalı: AYARLAR/FILM_AYAR.json içinde izinler.gece_flow açık değil. Varsayılan kip: elle.", kod="ortam")

    def calis(self):
        asamalar = ["gorsel"] if self.args.get("asama", "hepsi") == "hepsi" else [self.args["asama"]]
        if "video" in asamalar: self.v1_video_yok()            # Chrome açılmadan: v1'de video gönderimi yok (4)
        self.on_kosullar(); flow_kilidi_al(self.film)
        ES = 0x80000000 | 0x00000001
        try: ctypes.windll.kernel32.SetThreadExecutionState(ES)   # çalışırken uyku yok
        except Exception: pass
        self.chrome_ac(); self.giris_kontrol(); self.hesap_denetle(); self.projeye_git()
        partiler = sorted({s.get("parti", 1) for s in self.sahneler()})
        if self.args.get("parti"): partiler = [p for p in partiler if p in self.args["parti"]]
        self.log(f"BAŞLADI · film {self.film} · kip {self.A['kip']} · partiler {partiler} · aşama {asamalar}")
        self.bildir(f"Başladı ({self.A['kip']}): partiler {partiler}, aşama {'+'.join(asamalar)}")
        for i, p in enumerate(partiler, 1):
            for tur in asamalar: self.asama(tur, self.sahneler(p))
            self.bildir(f"Parti {p} bitti.")
            if self.parti_bitti() and i < len(partiler):
                self.tempo_bekle(); self.projeye_git()
        try:
            import kontrol
            f = kontrol.Film(self.root); f.reports(); f.save()
        except Exception as e: self.log("rapor hatası:", str(e)[:100])
        self.son_denetim()
        red = [n for n, v in self.D["sahne"].items() if "reddedildi" in (v.get("gorsel_durum"), v.get("video_durum"))]
        self.bildir("Üretim BİTTİ (v1: yalnız görsel)." + (f" Reddedilen sahneler: {', '.join(red)}" if red else " Reddedilen sahne yok."))

    def kurgu(self):
        """Zincirin sonu: seslendirme + CapCut projesi (render yok)."""
        videolu = [s for s in self.plan["sahneler"] if os.path.exists(os.path.join(self.sv, f"{s['no']:03d}.mp4"))]
        if not videolu: return
        for ad, betik in (("Seslendirme", "seslendir.py"), ("CapCut projesi", "capcut_film.py")):
            self.log(f"{ad} başlıyor...")
            r = subprocess.run([sys.executable, os.path.join(HERE, betik), self.root], capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            self.kayit.write(r.stdout[-4000:] + "\n" + r.stderr[-2000:] + "\n"); self.kayit.flush()
            if r.returncode != 0:
                self.bildir(f"{ad} hata verdi; MEMMET_KAYIT.txt'ye bak.", acil=True); return
        try:
            info = json.load(open(os.path.join(self.root, "KURGU", "son_capcut_projesi.json"), encoding="utf-8"))
            self.bildir(f"CapCut projesi hazır: {info['proje']} ({info['klip']} klip, {round(info['sure_sn'] / 60, 1)} dk). CapCut'ı aç, en üstte.")
        except Exception: self.bildir("CapCut projesi hazır.")


def uyari_var_mi(m):
    """Beklenmeyen hata / kesmede: sayfada uyarı var mı (salt okuma). Varsa mesaj, yoksa None."""
    if m is None or getattr(m, "page", None) is None: return UYARI_MESAJI if getattr(m, "uyari_goruldu", False) else None
    try: m.olagandisi_denetle()
    except Durdur as e: return str(e)
    except Exception: pass
    return None


def bitir(m, root, kod, mesaj):
    """Durdur sonrası: önce kilit ve çıkış dosyası (sayfaya dokunmadan), sonra bildirim. Çıkış kodunu döndürür."""
    if kod == "olagandisi":
        kilit_yaz(getattr(m, "film", os.path.basename(root)), mesaj)
    cikis_yaz(root, kod, mesaj)
    if m is not None:
        try: m.bildir(f"DURDU: {mesaj}", acil=True)
        except Exception: pass
    else: print("DURDU:", mesaj, flush=True)
    return CIKIS.get(kod, 2)


def telegram_test():
    A = ayar(); p = A.get("telegram_dosya")
    lines = [l.strip() for l in open(p, encoding="utf-8-sig") if l.strip()] if p and os.path.exists(p) else []
    if not lines: print("Telegram bot anahtarı yok. @BotFather'dan aldığın anahtarı şu dosyanın İLK SATIRINA yapıştır:", p); return
    tok = lines[0]
    if len(lines) < 2:   # sohbet numarasını bota yazılan son mesajdan bul
        r = json.load(urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/getUpdates", timeout=20))
        ids = [u["message"]["chat"]["id"] for u in r.get("result", []) if "message" in u]
        if not ids: print("Önce telefondan bota bir mesaj yaz (örn. 'merhaba'), sonra tekrar çalıştır."); return
        open(p, "a", encoding="utf-8").write(f"\n{ids[-1]}\n"); lines.append(str(ids[-1])); print("Sohbet numarası kaydedildi.")
    data = urllib.parse.urlencode({"chat_id": lines[1], "text": "🎬 Memmet Auto bağlandı. Bildirimler buraya gelecek."}).encode()
    urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/sendMessage", data, timeout=20); print("Deneme mesajı gönderildi.")


def argumanlar(a):
    """Komut satırı → (kök, args). Kök ilk konumsal argüman ya da --film (film.py sözleşmesi)."""
    bayrak = {"--giris": "giris", "--bakiye": "bakiye", "--kurgu-yok": "kurgu_yok"}
    args = {"asama": "hepsi", "mod": "elle"}; root = None; i = 0
    while i < len(a):
        k = a[i]
        if k in bayrak: args[bayrak[k]] = True
        elif k in ("--asama", "--parti", "--sahne", "--mod", "--film", "--blok", "--onizleme") and i + 1 < len(a):
            v = a[i + 1]; i += 1
            if k == "--film": root = root or v
            elif k in ("--parti", "--sahne"): args[k[2:]] = [int(x) for x in v.split(",")]
            else: args[k[2:]] = v
        elif not k.startswith("--") and root is None: root = k
        i += 1
    return root, args


def main(a=None):
    a = sys.argv[1:] if a is None else a
    if not a: print(__doc__); return
    if "--telegram-test" in a: telegram_test(); return
    root, args = argumanlar(a)
    if not root: print(__doc__); sys.exit(4)
    m = None
    try:
        m = Memmet(root, args)
        if args.get("giris") or args.get("bakiye"):
            m.on_kosullar(); m.chrome_ac(); m.giris_kontrol(bekle_giris=bool(args.get("giris"))); m.hesap_denetle()
            m.son_denetim()
            if args.get("bakiye"):
                b = m.bakiye_oku(); cikis_yaz(root, "tamam", "bakiye", {"bakiye_okunan": b}); return
            m.log("Giriş tamam. Bu pencereyi açık bırakabilir ya da kapatabilirsin."); cikis_yaz(root, "tamam", "giriş"); return
        if args.get("blok"):
            o = m.blok_calis(); cikis_yaz(root, "tamam", f"blok {m.blok_id} bitti", o); return
        m.calis(); cikis_yaz(root, "tamam", "bitti")
    except Durdur as e:
        if e.kod != "olagandisi" and m is not None and m.page is not None:
            try: m.olagandisi_denetle()      # başka bir nedenle duruyorsak bile uyarı varsa uyarı olarak kaydedilir
            except Durdur as e2: e = e2
        if m is not None and m.ozet: cikis_yaz(root, e.kod, str(e), m.ozet)
        sys.exit(bitir(m, root, e.kod, str(e)))
    except KeyboardInterrupt:
        if m: m.log("Kullanıcı durdurdu.")
        u = uyari_var_mi(m)
        if u: sys.exit(bitir(m, root, "olagandisi", u))
        cikis_yaz(root, "genel", "kullanıcı durdurdu"); sys.exit(2)
    except Exception:
        if m is None: raise
        m.log("BEKLENMEYEN HATA:\n" + traceback.format_exc())
        u = uyari_var_mi(m)                    # hata uyarının kendisinden olabilir (katman tıklamayı engelledi): önce salt okunur
        if u:
            if m.ozet: cikis_yaz(root, "olagandisi", u, m.ozet)
            sys.exit(bitir(m, root, "olagandisi", u))
        m.hata_kaydi("beklenmeyen")
        cikis_yaz(root, "beklenmeyen", "beklenmeyen hata", m.ozet)
        m.bildir("Beklenmeyen hata ile durdu. MEMMET_KAYIT.txt'ye bak.", acil=True); sys.exit(1)
    finally:
        if m: m.kapat()
        flow_kilidi_birak()


if __name__ == "__main__":
    main()
