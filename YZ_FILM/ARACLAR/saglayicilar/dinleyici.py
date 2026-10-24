"""DİNLEYİCİ sağlayıcısı — filmin sesini başka bir model ailesine dinletir, ses sorularını cevaplatır (TASARIM D-19, §5.6, [SON] K-3).

Sorular: karakter başına aksan (_SES/SES_PROFILLERI.json `aksan`), ses–yüz uyumu (yaş/cinsiyet tarifine uyuyor mu), müzik kalitesi
(ucuz/yapay mı, diyaloğu bastırıyor mu), yaratık sesi, metalik/robotik ses. Bulgu kaynağıdır (BAYRAK), onay kaynağı değildir.
Açılma kuralı izleyici ile aynıdır (anahtar + maliyet 0; O0e `ses_girisi` false → ÖLÇÜLEMEDİ). Ses videodan tek kanallı MP3 olarak
çıkarılır (geçici dosya). Anahtar yazdırılmaz.
Kullanım: python saglayicilar/dinleyici.py --kip animatik [--tur N] [--sahte] --film <film>
          → _RAPOR/SEYIRCI/<kip>_t<N>/dinleyici_rapor.json ({durum, cevaplar[{soru, cevap, guven}], bulgular[{zaman, tur, siddet, not}]})
"""
import os, sys, json, time, shutil, tempfile, subprocess, argparse
ARACLAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
import ortak
from saglayicilar import Saglayici, Kisitlandi
from saglayicilar.izleyici import GeminiIstemci, acik_mi, film_ayar, video_bul, sahte_mi, ANAHTAR_DOSYASI, ANAHTAR_ORTAM

SURUM = "dinleyici 1.0"
BULGU_TURLERI = ("aksan", "ses_yuz", "muzik", "yaratik", "metalik", "seviye", "anlasilmaz")


def sorular(film):
    prof = ortak.json_oku(os.path.join(film, "_SES", "SES_PROFILLERI.json"), {}) or {}
    kar = prof.get("karakterler") if isinstance(prof.get("karakterler"), dict) else prof
    out = []
    for kid, p in (kar or {}).items():
        if not isinstance(p, dict): continue
        et = p.get("ses_etiketi_tr") or p.get("veo_ses_tarifi") or kid
        if p.get("aksan"): out.append({"id": "aksan_%s" % kid, "soru": "Does the voice described as '%s' keep a %s accent throughout?" % (et, p["aksan"])})
        if p.get("veo_ses_tarifi"):
            out.append({"id": "ses_yuz_%s" % kid, "soru": "Does the voice '%s' sound like: %s?" % (et, p["veo_ses_tarifi"])})
    out += [{"id": "muzik_kalite", "soru": "Does the music sound cheap, synthetic or looped? Does it ever mask dialogue?"},
            {"id": "metalik", "soru": "Do any voices sound metallic, robotic or processed?"},
            {"id": "yaratik", "soru": "If a creature is heard, is its sound believable and consistent?"}]
    return out


DINLE_ISTEMI = """You are a sound supervisor listening blind to a film draft's mix. Answer ONLY with JSON:
{{"cevaplar": [{{"soru": "<id>", "cevap": "evet|hayir|kismen|duyulmadi", "guven": 0-1, "not": "..."}}],
 "bulgular": [{{"zaman": "mm:ss", "tur": "aksan|ses_yuz|muzik|yaratik|metalik|seviye|anlasilmaz", "siddet": 1-3, "not": "..."}}]}}
Questions (id: question):
{sorular}"""


def normal(j):
    j = j if isinstance(j, dict) else {}
    c = [{"soru": str(x.get("soru")), "cevap": str(x.get("cevap")), "guven": x.get("guven"), "not": str(x.get("not") or "")[:300]}
         for x in j.get("cevaplar") or [] if isinstance(x, dict)]
    b = [{"zaman": str(x.get("zaman")), "tur": x.get("tur"), "siddet": x.get("siddet"), "not": str(x.get("not") or "")[:300]}
         for x in j.get("bulgular") or [] if isinstance(x, dict) and x.get("tur") in BULGU_TURLERI]
    return {"cevaplar": c[:60], "bulgular": b[:100]}


class Dinleyici(Saglayici):
    ad = "dinleyici"
    turler = ("dinleyici",)
    kredili = False

    def hazir(self):
        ok, neden, _ = acik_mi(self, "ses")
        return ok, neden or ""

    def dinle(self, film, video, kip, tur):
        k = self.anahtar(ANAHTAR_DOSYASI, ANAHTAR_ORTAM)
        if not k: raise Kisitlandi("Gemini anahtarı yok", kod="anahtar")
        d = tempfile.mkdtemp(prefix="yz_dinle_")
        try:
            ses = os.path.join(d, "ses.mp3")
            r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-b:a", "64k", ses], capture_output=True)
            if r.returncode != 0: raise Kisitlandi("ses çıkarılamadı", kod="hazir_degil")
            ist = GeminiIstemci(k, (film_ayar().get("modeller") or {}).get("dinleyici"))
            f = ist.yukle(ses, "audio/mpeg")
            sq = sorular(film)
            j = ist.uret([{"file_data": {"mime_type": f["mime"], "file_uri": f["uri"]}},
                          {"text": DINLE_ISTEMI.format(sorular="\n".join("%s: %s" % (s["id"], s["soru"]) for s in sq))}])
            return normal(j)
        finally: shutil.rmtree(d, ignore_errors=True)


class SahteDinleyici(Dinleyici):
    ad = "sahte_dinleyici"

    def hazir(self): return True, ""

    def dinle(self, film, video, kip, tur):
        return normal({"cevaplar": [{"soru": s["id"], "cevap": "evet", "guven": 0.5} for s in sorular(film)],
                       "bulgular": [{"zaman": "00:02", "tur": "muzik", "siddet": 1, "not": "sahte bulgu"}]})


def calistir(film, kip, tur, sahte=None, saglayici=None):
    film = os.path.abspath(film)
    hedef = os.path.join(film, "_RAPOR", "SEYIRCI", "%s_t%d" % (kip, tur), "dinleyici_rapor.json")
    s = saglayici or (SahteDinleyici() if (sahte if sahte is not None else sahte_mi(film)) else Dinleyici())
    k = {"_surum": 1, "saglayici": s.ad, "arac_surum": SURUM, "zaman": time.strftime("%Y-%m-%dT%H:%M:%S")}
    video = video_bul(film, kip, tur); ok, neden = s.hazir()
    if not video: k.update(durum="olculemedi", neden="video yok")
    elif not ok: k.update(durum="olculemedi", neden=neden)
    else:
        try: k.update(durum="olculdu", **s.dinle(film, video, kip, tur))
        except Kisitlandi as e: k.update(durum="olculemedi", neden=str(e), kod=e.kod)
        except (ValueError, KeyError) as e: k.update(durum="olculemedi", neden="cevap okunamadı (%s)" % e.__class__.__name__)
    ortak.atomik_yaz(hedef, k)
    return k


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(); ap.add_argument("--kip", default="animatik"); ap.add_argument("--tur", type=int, default=1)
    ap.add_argument("--film"); ap.add_argument("--sahte", action="store_true"); ap.add_argument("--saglayici")
    o = ap.parse_args(argv)
    if not o.film or not os.path.isdir(o.film): print("!! --film gerekli"); return 1
    k = calistir(o.film, o.kip, o.tur, sahte=True if (o.sahte or o.saglayici == "sahte") else None)
    print(json.dumps({"durum": k["durum"], "neden": k.get("neden")}, ensure_ascii=False)); return 0


if __name__ == "__main__":
    sys.exit(main())
