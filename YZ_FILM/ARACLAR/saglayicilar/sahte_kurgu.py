"""SAHTE KURGU — video sonrası ses ve kurgu türleri için ağsız, kredisiz test sağlayıcısı (TASARIM §6.10, ADLAR saglayici_turleri).

Türler: ayristirma, asr, ses_donustur, dudak, buyutme, agiz (ağız açıklığı dizisi), yuz_kimligi, dinleyici.
Bozuk girdi fikstürleri (testlerin enjekte ettiği hatalar) film klasörünün _SAHTE/ altından okunur:
  _SAHTE/asr/<ad>.json          {"metin": "...", "kelimeler": [{"w","bas","bit"}]}  — yoksa bilinen metin, sesli bölgeye yayılır
  _SAHTE/donusum.json           {"<replik>": {"benzerlik": 0.58, "gecikme_ms": 5, "wer_artis": 0.0}}
  _SAHTE/agiz/<plan>.json       {"fps": 24, "yuzler": {"<karakter>": [açıklık, …]}} (klip zamanı) — yoksa klip sesinin zarfından
  _SAHTE/yuz.json               {"<plan>": "<konuşan yüz>"}
Bu sağlayıcı ses ya da görüntü üretmez gibi davranmaz: dönüştürücü girdi sesini (istenen gecikmeyle) çıktıya kopyalar, büyütücü Lanczos'tur.
"""
import os, sys, json, shutil
import numpy as np
ARACLAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
from saglayicilar import Saglayici, Kisitlandi
import ortak


def _fikstur(film, *yol):
    return ortak.json_oku(os.path.join(film, "_SAHTE", *yol)) if film else None


class SahteKurgu(Saglayici):
    ad = "sahte"
    turler = ("ayristirma", "asr", "ses_donustur", "dudak", "buyutme", "agiz", "yuz_kimligi", "dinleyici")
    kredili = False
    ortam = "her_ikisi"
    elle = False

    def ayristir(self, film, klip, cikti_dir, ad=None):
        import kurgu_ortak as ko
        a = ko.video_sesi(klip)
        if a is None: raise Kisitlandi("klipte ses yok", kod="hazir_degil")
        ad = ad or os.path.splitext(os.path.basename(klip))[0]
        k = ko.wav_yaz(os.path.join(cikti_dir, f"{ad}_konusma.wav"), a)
        d = ko.wav_yaz(os.path.join(cikti_dir, f"{ad}_diger.wav"), a * 0.05)
        return {"konusma": k, "diger": d}

    def asr(self, film, wav, bilinen_metin=None, ad=None):
        import kurgu_ortak as ko
        f = _fikstur(film, "asr", f"{ad or os.path.splitext(os.path.basename(wav))[0]}.json")
        if isinstance(f, dict): return {"metin": f.get("metin", ""), "kelimeler": f.get("kelimeler") or [], "guven": f.get("guven", 0.9)}
        a, sr = ko.wav_oku(wav); z = ko.zarf(a, sr, 100)
        if not len(z) or z.max() < 0.01: return {"metin": "", "kelimeler": [], "guven": 0.0}
        ses = np.where(z > 0.25 * z.max())[0]; bas, bit = ses[0] / 100.0, (ses[-1] + 1) / 100.0
        ks = (bilinen_metin or "").split()
        if not ks: return {"metin": "", "kelimeler": [], "guven": 0.5}
        d = (bit - bas) / len(ks)
        return {"metin": " ".join(ks), "kelimeler": [{"w": w, "bas": round(bas + i * d, 3), "bit": round(bas + (i + 1) * d, 3)}
                                                     for i, w in enumerate(ks)], "guven": 0.9}

    def ses_donustur(self, film, giris_wav, karakter, cikti, f0_yt=0, replik=None):
        import kurgu_ortak as ko
        f = (_fikstur(film, "donusum.json") or {}).get(replik or "", {})
        a, sr = ko.wav_oku(giris_wav); g = int(sr * float(f.get("gecikme_ms", 4)) / 1000)
        b = np.concatenate([np.zeros(max(g, 0), np.float32), a])[:len(a)]
        ko.wav_yaz(cikti, b, sr)
        return {"benzerlik": f.get("benzerlik", 0.82), "wer_artis": f.get("wer_artis", 0.0), "motor": "sahte"}

    def dudak(self, film, klip, ses_wav, pencere, cikti):
        shutil.copyfile(klip, cikti)
        return {"sure_sn": None, "motor": "sahte"}

    def buyut(self, film, giris, cikti, olcek=2):
        import kurgu_ortak as ko
        ko.ffmpeg("-i", giris, "-vf", f"scale=iw*{olcek}:ih*{olcek}:flags=lanczos", "-c:v", "libx264", "-preset", "ultrafast",
                  "-pix_fmt", "yuv420p", "-c:a", "copy", cikti)
        return {"motor": "lanczos", "yz": False}

    def agiz_dizisi(self, film, klip, plan, karakterler=()):
        """{"fps", "yuzler": {id: [0..1 açıklık]}} klip zamanında. Fikstür yoksa klip sesinin zarfı (ilk karakterin ağzı)."""
        import kurgu_ortak as ko
        f = _fikstur(film, "agiz", f"{plan}.json")
        if isinstance(f, dict): return f
        a = ko.video_sesi(klip)
        if a is None: return None
        z = ko.zarf(a, ko.SR, ko.FPS); z = z / (z.max() or 1.0)
        yuz = {k: ([round(float(x), 4) for x in z] if i == 0 else [0.0] * len(z)) for i, k in enumerate(karakterler)}
        return {"fps": ko.FPS, "yuzler": yuz}

    def yuz_kimligi(self, film, klip, plan, t=None):
        f = _fikstur(film, "yuz.json") or {}
        return f.get(str(plan))

    def dinleyici(self, film, wav, soru, secenekler):
        raise Kisitlandi("sahte dinleyici yanıt vermez (ölçülemedi)", kod="anahtar")
