"""FLOW sağlayıcısı — Google Flow'da görsel ve video üretimini Memmet'e (memmet.py) yaptırır.
Toplu çalışır: Memmet partileri kendi temposunda yürütür, sonuçları SIRALI_GORSEL / SIRALI_VIDEO'ya indirir.
Memmet'in çıkış kodu (ve film klasöründeki _memmet_cikis.json) Kisitlandi(kod)'a çevrilir:
  7 → olagandisi (Flow uyarısı)   2 → dogrulama / giris / kredi / arayuz   4 → ortam (sürüm, izin)
Kredi dışındaki hiçbir kısıtta başka sağlayıcıya geçilmez; kodu bilinmeyen çıkış da geçiş yapmaz. Atlatma denenmez.
"""
import os, sys, json, subprocess
from saglayicilar import Saglayici, Kisitlandi, ARACLAR


class Flow(Saglayici):
    ad = "flow"
    turler = ("gorsel", "video")
    toplu_mu = True

    def hazir(self):
        try: import playwright  # noqa: F401
        except ImportError: return False, "playwright kurulu değil (KURULUM.bat)"
        return True, ""

    def toplu(self, film, tur, sahneler):
        nos = ",".join(str(s["no"]) for s in sahneler)
        cmd = [sys.executable, os.path.join(ARACLAR, "memmet.py"), film, "--asama", tur, "--kurgu-yok", "--sahne", nos]
        cikis_dosya = os.path.join(film, "_memmet_cikis.json")
        if os.path.exists(cikis_dosya): os.remove(cikis_dosya)
        r = subprocess.run(cmd)
        if r.returncode == 0: return
        raise cikis_cevir(r.returncode, cikis_dosya)


KOD = {7: "olagandisi", 2: "dogrulama", 4: "ortam"}


def cikis_cevir(rc, cikis_dosya=None):
    """Memmet çıkışı → Kisitlandi. Dosyadaki kod, çıkış koduyla tutarlıysa daha ayrıntılıdır (2 → giris/kredi/arayuz...)."""
    kod, mesaj = KOD.get(rc, "bilinmeyen"), ""
    try:
        d = json.load(open(cikis_dosya, encoding="utf-8")) if cikis_dosya else {}
        if d.get("cikis") == rc and d.get("kod"): kod = d["kod"]
        mesaj = d.get("mesaj", "")
    except (OSError, ValueError): pass
    if rc == 7 and kod != "kilitli": kod = "olagandisi"   # 7 her zaman uyarı (ya da var olan kilit); dosya ne derse desin
    return Kisitlandi(f"Memmet durdu (çıkış {rc}, {kod}). {mesaj} MEMMET_KAYIT.txt'ye bak.".strip(), kod=kod)
