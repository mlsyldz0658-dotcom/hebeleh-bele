"""GEMİNİ API sağlayıcısı — Google AI Studio (Gemini API): gözlemci (ikinci göz, yalnız BAYRAK), izleyici (MP4), dinleyici (WAV), görsel
(yalnız Ö0-e uygun bulduysa) (TASARIM D-19, D-41, §5.6).

Açılma kuralı (D-19, [SON] K-3) — izin_karari(tur):
  - anahtar <veri>/AYARLAR/gemini_anahtar.txt'de (ya da GEMINI_API_KEY ortam değişkeninde) yoksa → kapalı, "ölçülemedi" (çağıran BAYRAK yazar ve
    izle-dinle bilgi paketi verir).
  - katman (Ö0-e: <veri>/BILGI/OLCUM0/O0e.json → gemini_katman; yoksa AYARLAR/GEMINI_DURUMU.json) "ucretli" değilse çağrının maliyeti 0'dır →
    gozlemci/izleyici/dinleyici AÇIK (FILM_AYAR usd_tavan_film 0 olsa bile; ücretsiz anahtar faturalandırmasız alınır, §8.2).
  - katman "ucretli" ise yalnız izinler.gemini_api_ucretli = true VE butce.usd_tavan_film > 0 ile açık.
  - gorsel türü ek olarak Ö0-e'nin "gorsel_uygun: true" kararını ister (yoksa kapalı; paket yolu sürer).
  - Ö0-e "video_giris: false" / "ses_giris: false" dediyse izleyici / dinleyici kapalı ("ücretsiz katman video/ses girişini kabul etmiyor").
Hatalar → Kisitlandi: 429/RESOURCE_EXHAUSTED → kota · 401/403 → anahtar · ağ → ag · güvenlik reddi → filtre_red · diğer → bilinmeyen.
  Kota dolunca çağıran (D-19) dikey kesit ve son kurgu için bir kez 8 BEKLE ile bekler; öteki çağrılar ÖLÇÜLEMEDİ olur.
Anahtar yalnız istek başlığında (x-goog-api-key) gider; asla URL'ye, loga, rapora yazılmaz. Kullanım kaydı <veri>/HESAP/GEMINI_KULLANIM.jsonl
(zaman, tür, model, bayt, sonuç; anahtar yok). Model adları bellekten (doğrulanacak; FILM_AYAR "gemini": {"model_gozlem", "model_gorsel"}).
Kodda: from saglayicilar import gemini_api as ga
  ga.izin_karari("dinleyici") → (acik, neden) · s = ga.GeminiAPI(tasiyici=None) · s.dinle(wav, istem) → dict · s.izle(mp4, istem) → dict
  s.gozlem([jpg…], istem) → dict · s.gorsel(film, sahne, cikti) · ga.olculemedi_kaydi(tur, neden) → ölçüm maddesi
"""
import os, sys, json, base64, datetime, mimetypes
from saglayicilar import Saglayici, Kisitlandi, ARACLAR
import ortak

ANAHTAR_DOSYA, ANAHTAR_ORTAM = "gemini_anahtar.txt", "GEMINI_API_KEY"
URL = "https://generativelanguage.googleapis.com/v1beta"
MODEL_GOZLEM, MODEL_GORSEL = "gemini-2.5-flash", "gemini-2.5-flash-image"
TURLER_API = ("gozlemci", "izleyici", "dinleyici", "gorsel")
SATIR_ICI_MAX = 18 * 1024 * 1024


def _ayar():
    try: return ortak.json_oku(os.path.join(ortak.yollar()["ayarlar"], "FILM_AYAR.json"), {}) or {}
    except ortak.YolYok: return {}


def o0e():
    try: v = ortak.yollar()["veri_kok"]
    except ortak.YolYok: return {}
    o = ortak.json_oku(os.path.join(v, "BILGI", "OLCUM0", "O0e.json"), {}) or {}
    if not o.get("gemini_katman"):
        d = ortak.json_oku(os.path.join(v, "AYARLAR", "GEMINI_DURUMU.json"), {}) or {}
        if d.get("gemini_katman"): o = dict(o, gemini_katman=d["gemini_katman"])
    return o


def anahtar_var():
    """Anahtarın VARLIĞI (içerik okunmaz, boyut > 0 yeter) ya da ortam değişkeni."""
    if os.environ.get(ANAHTAR_ORTAM): return True
    try: p = os.path.join(ortak.yollar()["ayarlar"], ANAHTAR_DOSYA)
    except ortak.YolYok: return False
    return os.path.isfile(p) and os.path.getsize(p) > 0


def izin_karari(tur):
    if tur not in TURLER_API: return False, f"gemini_api {tur} türünü yapmaz"
    if not anahtar_var(): return False, "Gemini anahtarı yok (AYARLAR/gemini_anahtar.txt boş): ölçülemedi; izle-dinle bilgi paketi verilir"
    o = o0e(); a = _ayar(); katman = o.get("gemini_katman") or "bilinmiyor"
    if katman == "ucretli":
        izin = bool((a.get("izinler") or {}).get("gemini_api_ucretli")); tavan = (a.get("butce") or {}).get("usd_tavan_film") or 0
        if not (izin and tavan > 0): return False, "Gemini katmanı ücretli; izinler.gemini_api_ucretli ve usd_tavan_film > 0 yok"
    if tur == "izleyici" and o.get("video_giris") is False: return False, "ücretsiz katman video girişini kabul etmiyor (Ö0-e): ölçülemedi"
    if tur == "dinleyici" and o.get("ses_giris") is False: return False, "ücretsiz katman ses girişini kabul etmiyor (Ö0-e): ölçülemedi"
    if tur == "gorsel" and not o.get("gorsel_uygun"): return False, "Ö0-e görsel kotasını uygun bulmadı (ya da ölçülmedi): paket yolu"
    return True, "ucretsiz" if katman != "ucretli" else "ucretli_izinli"


def olculemedi_kaydi(tur, neden, plan=None):
    m = {"madde": f"{tur}_gemini", "seviye": "OLCULEMEDI", "neden": neden, "bilgi_paketi": True}
    if plan is not None: m["plan"] = plan
    return m


def _http(yontem, url, govde, basliklar, zaman_asimi=180):
    import urllib.request, urllib.error
    istek = urllib.request.Request(url, data=govde, method=yontem, headers=basliklar)
    try:
        with urllib.request.urlopen(istek, timeout=zaman_asimi) as r: return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e: return e.code, e.read(), dict(e.headers or {})
    except (urllib.error.URLError, OSError) as e: raise Kisitlandi(f"Gemini API'ye ulaşılamadı ({e.__class__.__name__})", kod="ag")


class GeminiAPI(Saglayici):
    ad = "gemini_api"
    turler = TURLER_API
    kredili = False                        # ücretsiz katmanda maliyet 0 (D-19); ücretli kullanım izin + dolar tavanıyla
    elle = False

    def __init__(self, tasiyici=None):
        self.tasiyici = tasiyici or _http
        g = (_ayar().get("gemini") or {})
        self.model_gozlem = g.get("model_gozlem") or MODEL_GOZLEM
        self.model_gorsel = g.get("model_gorsel") or MODEL_GORSEL

    def hazir(self, tur="gozlemci"):
        return izin_karari(tur)

    def _anahtar(self):
        k = self.anahtar(ANAHTAR_DOSYA, ANAHTAR_ORTAM)
        if not k: raise Kisitlandi("Gemini anahtarı yok", kod="anahtar")
        return k

    def _kayit(self, tur, model, bayt, sonuc):
        try:
            p = os.path.join(ortak.yollar()["hesap"], "GEMINI_KULLANIM.jsonl"); os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "a", encoding="utf-8") as f:
                f.write(json.dumps({"zaman": datetime.datetime.now().astimezone().isoformat(timespec="seconds"), "tur": tur, "model": model,
                                    "bayt": bayt, "sonuc": sonuc}, ensure_ascii=False) + "\n")
        except Exception: pass

    def _cagir(self, tur, model, parcalar, json_cevap=True):
        acik, neden = izin_karari(tur)
        if not acik: raise Kisitlandi(neden, kod="anahtar" if "anahtar" in neden.lower() else "hazir_degil")
        govde = {"contents": [{"role": "user", "parts": parcalar}]}
        if json_cevap: govde["generationConfig"] = {"responseMimeType": "application/json"}
        veri = json.dumps(govde).encode("utf-8")
        st, cevap, _ = self.tasiyici("POST", f"{URL}/models/{model}:generateContent", veri,
                                     {"Content-Type": "application/json", "x-goog-api-key": self._anahtar()})
        self._kayit(tur, model, len(veri), st)
        if st == 429: raise Kisitlandi("Gemini kotası doldu", kod="kota")
        if st in (401, 403): raise Kisitlandi("Gemini anahtarı geçersiz ya da yetkisiz", kod="anahtar")
        if st >= 400: raise Kisitlandi(f"Gemini API hata {st}", kod="bilinmeyen")
        j = json.loads(cevap.decode("utf-8"))
        aday = (j.get("candidates") or [{}])[0]
        if aday.get("finishReason") in ("SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST") or (j.get("promptFeedback") or {}).get("blockReason"):
            raise Kisitlandi("Gemini güvenlik filtresi reddetti", kod="filtre_red")
        return aday.get("content", {}).get("parts") or []

    def _dosya_parcasi(self, yol):
        mt = mimetypes.guess_type(yol)[0] or "application/octet-stream"
        boy = os.path.getsize(yol)
        if boy <= SATIR_ICI_MAX:
            with open(yol, "rb") as f: return {"inline_data": {"mime_type": mt, "data": base64.b64encode(f.read()).decode("ascii")}}
        st, cevap, bas = self.tasiyici("POST", f"{URL.replace('/v1beta', '')}/upload/v1beta/files", open(yol, "rb").read(),
                                       {"Content-Type": mt, "X-Goog-Upload-Protocol": "raw", "x-goog-api-key": self._anahtar()})
        if st == 429: raise Kisitlandi("Gemini kotası doldu", kod="kota")
        if st >= 400: raise Kisitlandi(f"Gemini dosya yükleme hata {st}", kod="bilinmeyen")
        f = json.loads(cevap.decode("utf-8")).get("file") or {}
        return {"file_data": {"mime_type": mt, "file_uri": f.get("uri")}}

    @staticmethod
    def _json(parcalar):
        metin = "".join(p.get("text", "") for p in parcalar)
        try: return json.loads(metin)
        except ValueError: return {"ham": metin[:4000], "cozulemedi": True}

    def gozlem(self, gorseller, istem):
        return self._json(self._cagir("gozlemci", self.model_gozlem, [self._dosya_parcasi(g) for g in gorseller] + [{"text": istem}]))

    def izle(self, mp4, istem):
        return self._json(self._cagir("izleyici", self.model_gozlem, [self._dosya_parcasi(mp4), {"text": istem}]))

    def dinle(self, wav, istem):
        return self._json(self._cagir("dinleyici", self.model_gozlem, [self._dosya_parcasi(wav), {"text": istem}]))

    def gorsel(self, film, sahne, cikti, referanslar=()):
        parcalar = [self._dosya_parcasi(r) for r in referanslar if os.path.isfile(r)] + [{"text": sahne.get("gorsel_istem") or ""}]
        for p in self._cagir("gorsel", self.model_gorsel, parcalar, json_cevap=False):
            d = p.get("inline_data") or p.get("inlineData")
            if d and d.get("data"):
                tmp = cikti + ".tmp"
                with open(tmp, "wb") as f: f.write(base64.b64decode(d["data"]))
                os.replace(tmp, cikti); return cikti
        raise Kisitlandi("Gemini görsel döndürmedi", kod="bilinmeyen")
