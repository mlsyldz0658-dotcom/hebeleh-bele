"""GEMINI_MUZIK_PAKETI — zincirin SON basamağı, elle iş (elle = True; TASARIM D-25, D-41). Yalnız LISANSLAR.json'da gemini_muzik için
"ticari_youtube": "evet" yazılıysa açılır. İlk çağrıda istem listesini <film>/MUZIK/GEMINI_PAKET/istemler.json'a yazar ve
Kisitlandi("elle_bekliyor") verir (muzik_uret 2 KULLANICI ile durur: "istem listesini Gemini'ye ver, gelen dosyaları GELENLER'e koy");
dosyalar <film>/GELENLER/MUZIK_<ipucu>*.wav|mp3 olarak gelince onları aday olarak döndürür.
"""
import os, glob, json
from saglayicilar import Saglayici, Kisitlandi


class GeminiMuzikPaketi(Saglayici):
    ad = "gemini_muzik_paketi"
    turler = ("muzik",)
    kredili = False
    elle = True
    ortam = "yerel"
    model = "gemini (elle)"
    lisans = "Google hizmet koşulları (LISANSLAR.json gemini_muzik)"

    def hazir(self):
        from olcum import ses as O
        if O.lisans("gemini_muzik").get("ticari_youtube") != "evet":
            return False, "Gemini müzik koşulları doğrulanmadı (LISANSLAR.json gemini_muzik ticari_youtube ≠ evet; D-25)"
        return True, ""

    def muzik(self, film, ipucu, cikti_dir, aday=3, referans_wav=None, motif=None):
        gelen = sorted(glob.glob(os.path.join(film, "GELENLER", f"MUZIK_{ipucu['id']}*.wav")) +
                       glob.glob(os.path.join(film, "GELENLER", f"MUZIK_{ipucu['id']}*.mp3")))
        if gelen: return gelen[:int(aday)]
        p = os.path.join(film, "MUZIK", "GEMINI_PAKET", "istemler.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        try:
            with open(p, encoding="utf-8") as f: d = json.load(f)
        except (OSError, ValueError): d = {"ipuclari": []}
        if not any(x.get("id") == ipucu["id"] for x in d["ipuclari"]):
            d["ipuclari"].append({"id": ipucu["id"], "istem": ipucu.get("istem_en"), "sure_sn": ipucu.get("hedef_sure_sn"),
                                  "dosya_adi": f"MUZIK_{ipucu['id']}_<n>.wav"})
            with open(p, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=1)
        raise Kisitlandi("Gemini müzik paketi kullanıcıyı bekliyor", kod="elle_bekliyor")
