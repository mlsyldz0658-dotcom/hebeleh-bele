"""İZLEYİCİ sağlayıcısı — render edilmiş MP4'ü (görüntü + ses) başka bir model ailesiyle izletir (TASARIM D-19, §5.6, [SON] K-3).

Zincir (§5.6): gemini_api → sahte. Bulgu kaynağıdır, onay kaynağı değildir: rapor seyirci şemasındadır (§5.8) + `yz_kusurlari[]
{zaman, tur: yuz|hareket|ses|dudak|muzik|goruntu, siddet}`; seyirci_topla bunu BAYRAK olarak ekler, medyana katmaz.
Açılma kuralı (D-19): <veri>/AYARLAR/gemini_anahtar.txt (ya da GEMINI_API_KEY) varsa ve maliyet 0 ise (O0e.json gemini_katman:
  ucretsiz; ölçülmediyse "bilinmiyor" → açık + BAYRAK katman_dogrulanmadi) AÇIK. Ücretli katmanda yalnız FILM_AYAR izinler.gemini_api_ucretli
  ve butce.usd_tavan_film > 0 ile. O0e'de video_girisi false → ÖLÇÜLEMEDİ. Kota (429) → Kisitlandi(kota). Anahtar yazdırılmaz, URL'ye
  konmaz (yalnız x-goog-api-key başlığı).
Kullanım:
  python saglayicilar/izleyici.py --kip animatik [--tur N] [--sahte] --film <film>
      → _RAPOR/SEYIRCI/<kip>_t<N>/izleyici_rapor.json  ({durum: olculdu|olculemedi, neden?, rapor?})
Kodda: from saglayicilar.izleyici import Izleyici, calistir, acik_mi, GeminiIstemci
"""
import os, sys, json, time, mimetypes, argparse, urllib.request, urllib.error
ARACLAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
import ortak
from saglayicilar import Saglayici, Kisitlandi

SURUM = "izleyici 1.0"
API = "https://generativelanguage.googleapis.com"
VARSAYILAN_MODEL = "gemini-2.5-flash"
KUSUR_TURLERI = ("yuz", "hareket", "ses", "dudak", "muzik", "goruntu")
ANAHTAR_DOSYASI, ANAHTAR_ORTAM = "gemini_anahtar.txt", "GEMINI_API_KEY"


def _veri():
    try: return ortak.yollar()
    except ortak.YolYok: return None


def o0e():
    y = _veri()
    return (ortak.json_oku(os.path.join(y["veri_kok"], "BILGI", "OLCUM0", "O0e.json"), {}) or {}) if y else {}


def film_ayar():
    y = _veri()
    return (ortak.json_oku(os.path.join(y["ayarlar"], "FILM_AYAR.json"), {}) or {}) if y else {}


def acik_mi(saglayici, giris="video"):
    """(açık_mı, neden, bayraklar). Anahtarın içeriği okunmaz, yalnız varlığı sorulur (anahtar() boş değilse)."""
    if not saglayici.anahtar(ANAHTAR_DOSYASI, ANAHTAR_ORTAM): return False, "Gemini anahtarı yok (kurulum §8.2 adım 3b)", []
    o = o0e(); bay = []
    if o.get(giris + "_girisi") is False: return False, "ücretsiz katman %s girişini kabul etmiyor (Ö0-e)" % giris, []
    katman = o.get("gemini_katman") or "bilinmiyor"
    if katman == "ucretli":
        a = film_ayar()
        if not ((a.get("izinler") or {}).get("gemini_api_ucretli") and float((a.get("butce") or {}).get("usd_tavan_film") or 0) > 0):
            return False, "Gemini katmanı ücretli; izin (gemini_api_ucretli) ve dolar tavanı yok", []
        bay.append("ucretli_katman")
    elif katman != "ucretsiz": bay.append("katman_dogrulanmadi")
    return True, None, bay


class GeminiIstemci:
    """Küçük REST istemcisi (stdlib). Dosya API'si ile yükler, ACTIVE olunca generateContent çağırır."""
    def __init__(self, anahtar, model=None, zaman_asimi=120):
        self._k = anahtar; self.model = model or VARSAYILAN_MODEL; self.za = zaman_asimi

    def _istek(self, url, veri=None, baslik=None, yontem=None):
        b = {"x-goog-api-key": self._k}; b.update(baslik or {})
        r = urllib.request.Request(url, data=veri, headers=b, method=yontem or ("POST" if veri is not None else "GET"))
        try:
            with urllib.request.urlopen(r, timeout=self.za) as y: return y.read(), dict(y.headers)
        except urllib.error.HTTPError as e:
            if e.code == 429: raise Kisitlandi("Gemini kotası doldu", kod="kota")
            if e.code in (401, 403): raise Kisitlandi("Gemini anahtarı reddedildi", kod="anahtar")
            raise Kisitlandi("Gemini HTTP %d" % e.code, kod="ag")
        except (urllib.error.URLError, OSError) as e: raise Kisitlandi("Gemini'ye ulaşılamadı (%s)" % e.__class__.__name__, kod="ag")

    def yukle(self, yol, mime=None):
        mime = mime or mimetypes.guess_type(yol)[0] or "application/octet-stream"
        boy = os.path.getsize(yol)
        _, h = self._istek(API + "/upload/v1beta/files", json.dumps({"file": {"display_name": os.path.basename(yol)}}).encode(),
                           {"X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start", "Content-Type": "application/json",
                            "X-Goog-Upload-Header-Content-Length": str(boy), "X-Goog-Upload-Header-Content-Type": mime})
        url = {k.lower(): v for k, v in h.items()}.get("x-goog-upload-url")
        if not url: raise Kisitlandi("Gemini yükleme adresi gelmedi", kod="ag")
        with open(yol, "rb") as f: veri = f.read()
        g, _ = self._istek(url, veri, {"X-Goog-Upload-Offset": "0", "X-Goog-Upload-Command": "upload, finalize",
                                       "Content-Length": str(boy)})
        dosya = json.loads(g.decode("utf-8")).get("file") or {}
        for _ in range(120):
            if dosya.get("state") in ("ACTIVE", None): break
            if dosya.get("state") == "FAILED": raise Kisitlandi("Gemini dosyayı işleyemedi", kod="ag")
            time.sleep(5)
            dosya = json.loads(self._istek(API + "/v1beta/" + dosya["name"])[0].decode("utf-8"))
        return {"uri": dosya.get("uri"), "mime": mime}

    def uret(self, parcalar, json_cevap=True):
        govde = {"contents": [{"role": "user", "parts": parcalar}]}
        if json_cevap: govde["generationConfig"] = {"responseMimeType": "application/json", "temperature": 0.4}
        g, _ = self._istek(API + "/v1beta/models/%s:generateContent" % self.model, json.dumps(govde).encode(), {"Content-Type": "application/json"})
        j = json.loads(g.decode("utf-8"))
        metin = "".join(p.get("text", "") for c in j.get("candidates") or [] for p in (c.get("content") or {}).get("parts") or [])
        return json.loads(metin) if json_cevap else metin


IZLE_ISTEMI = """You are a first-time YouTube viewer watching a fantasy film draft ({kip}). You know nothing about the plan or the writers' intentions.
Watch the whole video. Then answer ONLY with JSON of this shape:
{{"puanlar": {{"anlasilirlik": 1-10, "akicilik": 1-10, "merak": 1-10, "duygu": 1-10, "ritim": 1-10, "ilk30": 1-10, "GENEL": 1-10}},
 "kopukluklar": [{{"konum": {{"zaman": "mm:ss"}}, "tur": "KRITIK|ORTA|KUCUK", "neden": "..."}}],
 "sikilma": [{{"bas": "mm:ss", "bit": "mm:ss", "neden": "..."}}],
 "ilgi": [{{"konum": {{"zaman_bas": "mm:ss", "zaman_bit": "mm:ss"}}, "puan": 1-10}}],
 "acik_sorular": ["..."], "ozet_parti": "three sentences", "kapatma_ani": "mm:ss or null", "devam_olasiligi": 0-1, "devam": true,
 "yz_kusurlari": [{{"zaman": "mm:ss", "tur": "yuz|hareket|ses|dudak|muzik|goruntu", "siddet": 1-3, "not": "..."}}]}}
Rate harshly; do not be generous. yz_kusurlari = visible or audible AI-generation defects (morphing faces, floating motion, metallic voice,
lip mismatch, cheap music, image artefacts). One minute per ilgi entry."""


def rapor_normal(j, kip, tur):
    """Model cevabını seyirci şemasına (§5.8) indirger; şema dışı alanlar atılır."""
    j = j if isinstance(j, dict) else {}
    p = {k: v for k, v in (j.get("puanlar") or {}).items() if k in ("anlasilirlik", "akicilik", "merak", "duygu", "ritim", "ilk30", "GENEL")
         and isinstance(v, (int, float)) and 1 <= v <= 10}
    kus = [{"zaman": str(k.get("zaman")), "tur": k.get("tur"), "siddet": k.get("siddet"), "not": str(k.get("not") or "")[:300]}
           for k in j.get("yz_kusurlari") or [] if isinstance(k, dict) and k.get("tur") in KUSUR_TURLERI]
    return {"kip": kip, "tur": tur, "seyirci": None, "persona": None, "kaynak": "izleyici", "puanlar": p,
            "kopukluklar": [k for k in j.get("kopukluklar") or [] if isinstance(k, dict)][:50],
            "sikilma": [s for s in j.get("sikilma") or [] if isinstance(s, dict)][:50],
            "ilgi": [i for i in j.get("ilgi") or [] if isinstance(i, dict)][:200],
            "acik_sorular": [str(x) for x in j.get("acik_sorular") or []][:30], "ozet_parti": str(j.get("ozet_parti") or "")[:1200],
            "kapatma_ani": j.get("kapatma_ani"), "devam_olasiligi": j.get("devam_olasiligi"), "devam": bool(j.get("devam", True)),
            "yz_kusurlari": kus}


class Izleyici(Saglayici):
    ad = "izleyici"
    turler = ("izleyici",)
    kredili = False

    def hazir(self):
        ok, neden, _ = acik_mi(self, "video")
        return ok, neden or ""

    def izle(self, film, video, kip, tur):
        k = self.anahtar(ANAHTAR_DOSYASI, ANAHTAR_ORTAM)
        if not k: raise Kisitlandi("Gemini anahtarı yok", kod="anahtar")
        ist = GeminiIstemci(k, (film_ayar().get("modeller") or {}).get("izleyici"))
        f = ist.yukle(video)
        j = ist.uret([{"file_data": {"mime_type": f["mime"], "file_uri": f["uri"]}}, {"text": IZLE_ISTEMI.format(kip=kip)}])
        return rapor_normal(j, kip, tur)


class SahteIzleyici(Izleyici):
    """Test kipinde (D-41): ağsız, kararlı rapor."""
    ad = "sahte_izleyici"

    def hazir(self): return True, ""

    def izle(self, film, video, kip, tur):
        return rapor_normal({"puanlar": {"anlasilirlik": 7, "akicilik": 7, "merak": 7, "duygu": 6, "ritim": 7, "ilk30": 7, "GENEL": 7},
                             "kopukluklar": [], "acik_sorular": [], "ozet_parti": "sahte izleyici", "devam": True,
                             "yz_kusurlari": [{"zaman": "00:03", "tur": "hareket", "siddet": 1, "not": "sahte kusur"}]}, kip, tur)


def video_bul(film, kip, tur):
    import glob, re
    d = {"animatik": ("ANIMATIK", "animatik"), "kesit": ("KESIT", "kesit"), "kurgu": ("KURGU", "onizleme")}.get(kip)
    if not d: return None
    p = os.path.join(film, d[0], "%s_v%d.mp4" % (d[1], tur))
    if os.path.isfile(p): return p
    vs = sorted(glob.glob(os.path.join(film, d[0], "%s_v*.mp4" % d[1])), key=lambda x: int(re.search(r"_v(\d+)\.mp4$", x).group(1)))
    return vs[-1] if vs else None


def sahte_mi(film):
    m = ortak.json_oku(os.path.join(film, "HAZIRLIK.json"), {}) or {}
    return m.get("saglayici") == "sahte" or os.environ.get("YZ_FILM_IZLEYICI") == "sahte"


def calistir(film, kip, tur, sahte=None, saglayici=None):
    """İzleyiciyi koşturur; her durumda _RAPOR/SEYIRCI/<kip>_t<tur>/izleyici_rapor.json yazar. Hat beklemez: hata ÖLÇÜLEMEDİ olur."""
    film = os.path.abspath(film)
    hedef = os.path.join(film, "_RAPOR", "SEYIRCI", "%s_t%d" % (kip, tur), "izleyici_rapor.json")
    s = saglayici or (SahteIzleyici() if (sahte if sahte is not None else sahte_mi(film)) else Izleyici())
    _, _, bay = acik_mi(s) if not isinstance(s, SahteIzleyici) else (True, None, [])
    k = {"_surum": 1, "saglayici": s.ad, "arac_surum": SURUM, "zaman": time.strftime("%Y-%m-%dT%H:%M:%S"), "bayraklar": bay}
    video = video_bul(film, kip, tur)
    ok, neden = s.hazir()
    if not video: k.update(durum="olculemedi", neden="video yok")
    elif not ok: k.update(durum="olculemedi", neden=neden)
    else:
        try: k.update(durum="olculdu", rapor=s.izle(film, video, kip, tur), video=os.path.relpath(video, film).replace("\\", "/"))
        except Kisitlandi as e: k.update(durum="olculemedi", neden=str(e), kod=e.kod)
        except (ValueError, KeyError) as e: k.update(durum="olculemedi", neden="cevap okunamadı (%s)" % e.__class__.__name__)
    ortak.atomik_yaz(hedef, k)
    return k


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(); ap.add_argument("--kip", default="animatik"); ap.add_argument("--tur", type=int, default=1)
    ap.add_argument("--film"); ap.add_argument("--sahte", action="store_true"); ap.add_argument("--saglayici")
    o = ap.parse_args(argv)
    if not o.film or not os.path.isdir(o.film): print("!! --film gerekli"); return 1
    k = calistir(o.film, o.kip, o.tur, sahte=True if (o.sahte or o.saglayici == "sahte") else None)
    print(json.dumps({"durum": k["durum"], "neden": k.get("neden")}, ensure_ascii=False)); return 0


if __name__ == "__main__":
    sys.exit(main())
