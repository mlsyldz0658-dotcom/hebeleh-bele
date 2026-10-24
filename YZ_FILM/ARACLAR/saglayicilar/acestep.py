"""ACESTEP — ACE-Step 1.5 müzik sağlayıcısı (yerel, ayrı ortam KUR3; Py 3.11–3.12, CUDA). TASARIM D-25, §4.8.4, §5.6.
Ana süreç modeli yüklemez: iş dosyasını (<cikti_dir>/<ipucu>_acestep_is.json) yazar ve ayrı ortamın Python'uyla köprü betiğini çağırır:
  <YOLLAR.json ortamlar.acestep> <ARACLAR>/kopru/acestep_kopru.py <is.json>  → is.json'daki "ciktilar" yollarına wav'lar
İş: {istem_en, sure_sn, bpm, ton, olcu, aday, tohum, referans_wav (motifin çalınmış hâli; "Cover/Refer audio"), ciktilar[]}.
Ortam ya da köprü yoksa hazir() False (zincir sıradakine geçer; kart: "KUR3 ACE-Step ortamı yok"). 4 GB kartta tek ağır model kuralı:
GPU kuyruğu yerel_is.py'dedir; köprü zaman aşımı 30 dk/aday (tahmin; Ö0-c ölçer). Lisans: kod MIT (bellekten), ağırlık sayfası doğrulanacak.
"""
import os, json, subprocess
from saglayicilar import Saglayici, Kisitlandi

ARACLAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AceStep(Saglayici):
    ad = "acestep"
    turler = ("muzik",)
    kredili = False
    elle = False
    ortam = "yerel"
    model = "ACE-Step 1.5 (2B turbo)"
    lisans = "MIT (kod, bellekten); ağırlık lisansı LISANSLAR.json ace-step"
    zaman_asimi_sn = 1800

    def _py(self):
        import ortak
        try: return (ortak.yollar().get("ortamlar") or {}).get("acestep")
        except ortak.YolYok: return None

    def kopru(self): return os.path.join(ARACLAR, "kopru", "acestep_kopru.py")

    def hazir(self):
        py = self._py()
        if not (py and os.path.exists(py)): return False, "KUR3 ACE-Step ortamı yok (YOLLAR.json ortamlar.acestep)"
        if not os.path.exists(self.kopru()): return False, "ACE-Step köprüsü yok (kopru/acestep_kopru.py; P1)"
        return True, ""

    def muzik(self, film, ipucu, cikti_dir, aday=3, referans_wav=None, motif=None):
        ok, neden = self.hazir()
        if not ok: raise Kisitlandi(neden, kod="hazir_degil")
        os.makedirs(cikti_dir, exist_ok=True)
        cik = [os.path.join(cikti_dir, f"{ipucu['id']}_ace{i + 1}.wav") for i in range(int(aday))]
        is_ = {"istem_en": ipucu.get("istem_en"), "sure_sn": ipucu.get("hedef_sure_sn"), "bpm": ipucu.get("bpm") or (motif or {}).get("bpm"),
               "ton": ipucu.get("ton") or (motif or {}).get("ton"), "olcu": (motif or {}).get("olcu"), "aday": int(aday),
               "tohum": ipucu.get("tohum"), "referans_wav": referans_wav, "ciktilar": cik}
        p = os.path.join(cikti_dir, f"{ipucu['id']}_acestep_is.json")
        with open(p, "w", encoding="utf-8") as f: json.dump(is_, f, ensure_ascii=False, indent=1)
        try: r = subprocess.run([self._py(), self.kopru(), p], capture_output=True, text=True, timeout=self.zaman_asimi_sn * int(aday))
        except subprocess.TimeoutExpired: raise Kisitlandi("ACE-Step zaman aşımı", kod="hazir_degil") from None
        if r.returncode != 0: raise Kisitlandi(f"ACE-Step köprüsü hata verdi ({(r.stderr or '')[-120:]})", kod="hazir_degil")
        return [c for c in cik if os.path.exists(c)]
