"""FLOW sağlayıcısı — Google Flow'da görsel ve video üretimini Memmet'e (memmet.py) yaptırır.
Toplu çalışır: Memmet partileri kendi temposunda yürütür, sonuçları SIRALI_GORSEL / SIRALI_VIDEO'ya indirir.
Memmet'in çıkış kodu (ve film klasöründeki _memmet_cikis.json) Kisitlandi(kod)'a çevrilir:
  7 → olagandisi (Flow uyarısı)   2 → dogrulama / giris / kredi / arayuz   4 → ortam (sürüm, izin)
  5 → butce (BUTK bütçe noktası onay vermedi)   8 → bekle (toplanacak iş, başka Memmet açık: topla / mesgul)
Kredi dışındaki hiçbir kısıtta başka sağlayıcıya geçilmez; kodu bilinmeyen çıkış da geçiş yapmaz. 5 ve 8 HİÇBİR ZAMAN geçiş yapmaz:
bütçe reddi başka sağlayıcıda harcamaya, bekleme ikinci gönderime dönüşmez. Atlatma denenmez.
v2 filmleri (SAHNELER _surum ≥ 2) toplu() ile değil film.py görevleri (memmet.py --blok) ile yürür.
"""
import os, sys, json, subprocess
from saglayicilar import Saglayici, Kisitlandi, ARACLAR, GECILEBILIR


class Flow(Saglayici):
    ad = "flow"
    turler = ("gorsel", "video")
    toplu_mu = True

    def hazir(self):
        try: import playwright  # noqa: F401
        except ImportError: return False, "playwright kurulu değil (KURULUM.bat)"
        return True, ""

    def toplu(self, film, tur, sahneler):
        try: surum = int((json.load(open(os.path.join(film, "SAHNELER.json"), encoding="utf-8-sig")) or {}).get("_surum") or 1)
        except (OSError, ValueError, TypeError, AttributeError): surum = 1
        if surum >= 2:     # v2: blok + önizleme imzası + animatik imzası film.py görevinde; toplu yol göndermez
            raise Kisitlandi("v2 film (SAHNELER _surum ≥ 2): Flow film.py görevleriyle (memmet.py --blok) yürür.", kod="ortam")
        nos = ",".join(str(s["no"]) for s in sahneler)
        cmd = [sys.executable, os.path.join(ARACLAR, "memmet.py"), film, "--asama", tur, "--kurgu-yok", "--sahne", nos]
        cikis_dosya = os.path.join(film, "_memmet_cikis.json")
        if os.path.exists(cikis_dosya): os.remove(cikis_dosya)
        r = subprocess.run(cmd)
        if r.returncode == 0: return
        raise cikis_cevir(r.returncode, cikis_dosya)


KOD = {7: "olagandisi", 2: "dogrulama", 4: "ortam", 5: "butce", 8: "bekle"}
GECMEZ_CIKIS = (5, 7, 8)        # dosya ne derse desin geçilebilir koda dönmez


def cikis_cevir(rc, cikis_dosya=None):
    """Memmet çıkışı → Kisitlandi. Dosyadaki kod, çıkış koduyla tutarlıysa daha ayrıntılıdır (2 → giris/kredi/arayuz...)."""
    kod, mesaj = KOD.get(rc, "bilinmeyen"), ""
    try:
        d = json.load(open(cikis_dosya, encoding="utf-8")) if cikis_dosya else {}
        if d.get("cikis") == rc and d.get("kod"): kod = d["kod"]
        mesaj = d.get("mesaj", "")
    except (OSError, ValueError): pass
    if rc == 7 and kod != "kilitli": kod = "olagandisi"   # 7 her zaman uyarı (ya da var olan kilit); dosya ne derse desin
    elif rc in GECMEZ_CIKIS and kod in GECILEBILIR: kod = KOD[rc]
    return Kisitlandi(f"Memmet durdu (çıkış {rc}, {kod}). {mesaj} MEMMET_KAYIT.txt'ye bak.".strip(), kod=kod)
