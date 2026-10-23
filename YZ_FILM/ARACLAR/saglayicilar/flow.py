"""FLOW sağlayıcısı — Google Flow'da görsel ve video üretimini Memmet'e (memmet.py) yaptırır.
Toplu çalışır: Memmet partileri kendi temposunda yürütür, sonuçları SIRALI_GORSEL / SIRALI_VIDEO'ya indirir.
Memmet "olağan dışı etkinlik", kredi bitmesi ya da arayüz değişikliği görünce DURUR (çıkış kodu 2) →
burada Kisitlandi olur. Atlatma denenmez; zincirde başka sağlayıcı varsa o kullanılır, yoksa hat durur.
"""
import os, sys, subprocess
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
        r = subprocess.run(cmd)
        if r.returncode == 2: raise Kisitlandi("Memmet durdu (uyarı / kredi / arayüz). MEMMET_KAYIT.txt'ye bak.")
        if r.returncode != 0: raise RuntimeError(f"Memmet hata ile çıktı ({r.returncode}).")
