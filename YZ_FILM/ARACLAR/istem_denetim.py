"""İSTEM DENETİM — SAHNELER.json'u kredi harcamadan önce mekanik olarak denetler (kâğıt üstü kalite kapısı).

Kullanım: python istem_denetim.py <film_klasoru>
Kurallar CLAUDE_ICIN.md ve 03_DERSLER.md'den alındı:
  HATA  (hat durur) : eksik alan, aynı sahne no iki kez, tanımsız/dosyası olmayan referans, 3+ referans,
                      replik > 20 kelime ya da 8 sn'ye sığmıyor, bitis_karesi olmayan sahneye bakıyor
  UYARI (hat sürer) : video isteminde filtre riski olan kelime, "No music." yok, konuşanın sesi atanmamış,
                      klipte birden çok konuşan, risk kelimesi var ama *_yedek istem yok
Çıktı: _RAPOR/ISTEM_DENETIM.txt
"""
import os, sys, re, json
import ortak   # SAHNELER.json v2 koruması
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Video istemlerinde küçükler filtresine takılan kelimeler (03_DERSLER.md)
FILTRE_KELIMELERI = ["girl", "little", "child", "children", "kid", "kids", "baby", "toddler", "siblings", "frail",
                     "bed", "sleep", "sleeping", "cheek", "chest", "trembles", "trembling"]
YAS_IFADESI = re.compile(r"\b\d+\s*(?:-\s*)?(?:years?|yrs?)(?:\s*-\s*|\s+)old\b|\byear-old\b|\byoung\b", re.I)
# Şiddet/kan sahnelerinde yedek istem şart (CLAUDE_ICIN.md kural 4)
RISK_KELIMELERI = ["blood", "bloody", "corpse", "dead body", "kill", "killed", "stab", "gore", "wound"]
KONUSMA = re.compile(r"\b([A-Z][a-z]+)\b[^.\"]{0,40}?\b(?:says|whispers|shouts|asks|replies|yells|murmurs)\s*:", re.S)
KELIME_SN = 2.5        # İngilizce konuşma ≈ 2,5 kelime/sn
REPLIK_SN, REPLIK_KELIME, REF_EN_COK = 8.0, 20, 2


def kelimeler(s): return re.findall(r"[A-Za-z0-9']+", s or "")
def bul(metin, liste):
    t = (metin or "").lower()
    return [k for k in liste if re.search(r"\b" + re.escape(k) + r"\b", t)]


def denetle(plan, kok=None):
    """[(seviye, sahne_no|None, mesaj)] döner. seviye: HATA / UYARI."""
    out = []
    def h(n, m): out.append(("HATA", n, m))
    def u(n, m): out.append(("UYARI", n, m))
    kar = plan.get("karakterler") or {}
    for ad, k in kar.items():
        if kok and k.get("ref") and not os.path.exists(os.path.join(kok, k["ref"])):
            h(None, f"karakter '{ad}' referans dosyası yok: {k['ref']}")
    sahneler = plan.get("sahneler") or []
    if not sahneler: h(None, "sahne yok")
    nolar = [s.get("no") for s in sahneler]
    for n in sorted({x for x in nolar if nolar.count(x) > 1}): h(n, "aynı sahne numarası birden çok kez var")
    for s in sahneler:
        n = s.get("no")
        for alan in ("no", "parti", "gorsel_istem", "hareket_istem"):
            if not s.get(alan): h(n, f"'{alan}' boş")
        refs = s.get("referans") or []
        for r in refs:
            if r not in kar: h(n, f"referans '{r}' karakterler listesinde yok")
        if len(refs) > REF_EN_COK: h(n, f"{len(refs)} referans var; en çok {REF_EN_COK} (Flow yüzleri karıştırır)")
        if s.get("bitis_karesi") is not None and s["bitis_karesi"] not in nolar:
            h(n, f"bitis_karesi {s['bitis_karesi']} diye bir sahne yok")
        hi = s.get("hareket_istem") or ""
        if s.get("motor", "flow") == "flow":
            f = bul(hi, FILTRE_KELIMELERI) + YAS_IFADESI.findall(hi)
            if f: u(n, f"video isteminde filtre riski: {', '.join(f)} (eller/makro/'blanket-wrapped figure' gibi dolaylı anlat)")
        if hi and "no music" not in hi.lower(): u(n, "hareket isteminde \"No music.\" yok (müzik ayrı katmanda)")
        risk = bul(hi + " " + (s.get("gorsel_istem") or ""), RISK_KELIMELERI)
        if risk and not (s.get("hareket_istem_yedek") or s.get("gorsel_istem_yedek")):
            u(n, f"riskli kelime ({', '.join(risk)}) var ama *_yedek istem yok")
        konusanlar = {m.lower() for m in KONUSMA.findall(hi)}
        if len(konusanlar) > 1: u(n, f"klipte birden çok konuşan: {', '.join(sorted(konusanlar))} (her klipte tek kişi)")
        rep = s.get("replik")
        if rep:
            w = len(kelimeler(rep.get("metin")))
            if rep.get("karakter") not in kar: h(n, f"replik karakteri '{rep.get('karakter')}' tanımsız")
            elif not kar[rep["karakter"]].get("ses"): u(n, f"'{rep['karakter']}' için ses (voice_id) atanmamış; Flow sesi kalır")
            if w > REPLIK_KELIME: h(n, f"replik {w} kelime; en çok {REPLIK_KELIME}")
            elif w / KELIME_SN > REPLIK_SN: h(n, f"replik ≈{w / KELIME_SN:.1f} sn; 8 sn'lik klibe sığmaz")
    return out


def rapor(kok):
    kok = os.path.abspath(kok)
    plan = ortak.sahneler_oku(kok, "istem_denetim.py")
    bulgular = denetle(plan, kok)
    os.makedirs(os.path.join(kok, "_RAPOR"), exist_ok=True)
    satirlar = [f"{sv:5} {'S%03d' % n if n is not None else 'GENEL'}  {m}" for sv, n, m in bulgular]
    hata = sum(1 for b in bulgular if b[0] == "HATA")
    ozet = f"ÖZET | HATA: {hata} | UYARI: {len(bulgular) - hata} | SAHNE: {len(plan.get('sahneler') or [])}"
    open(os.path.join(kok, "_RAPOR", "ISTEM_DENETIM.txt"), "w", encoding="utf-8").write("\n".join(satirlar + ["", ozet]) + "\n")
    return bulgular, ozet


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(0)
    b, ozet = rapor(sys.argv[1])
    for sv, n, m in b: print(f"{sv:5} {'S%03d' % n if n is not None else 'GENEL'}  {m}")
    print(ozet); sys.exit(1 if any(x[0] == "HATA" for x in b) else 0)
