"""PUAN OKU — seyirci/jüri raporlarının sonundaki ÖZET satırını okur, eşiğe ulaşıldı mı söyler.

Kullanım: python puan_oku.py <rapor.md> [<rapor2.md> ...] [--esik 8]
Rapor biçimi (son satırlardan biri):  OZET | anlasilirlik: 7 | merak: 8 | duygu: 6 | ORTALAMA: 7.0 | KRITIK: 2
Birden çok rapor verilirse ORTALAMA'ların ortalaması alınır (seyirci puanları gürültülü, eğilim önemli).
Çıkış kodu: 0 eşik geçildi ve KRITIK yok · 3 eşik altında ya da KRITIK var · 1 ÖZET satırı bulunamadı
"""
import re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OZET = re.compile(r"^\s*\**\s*[OÖ]ZET\s*\|(.+)$", re.I | re.M)


def oku(yol):
    m = OZET.findall(open(yol, encoding="utf-8-sig").read())
    if not m: return None
    alanlar = {}
    for parca in m[-1].split("|"):
        if ":" in parca:
            k, v = parca.split(":", 1)
            try: alanlar[k.strip().lower()] = float(v.strip().split()[0].replace(",", "."))
            except (ValueError, IndexError): pass
    if "ortalama" not in alanlar:
        puanlar = [v for k, v in alanlar.items() if k != "kritik"]
        if puanlar: alanlar["ortalama"] = sum(puanlar) / len(puanlar)
    return alanlar


def main(a):
    esik = float(a[a.index("--esik") + 1]) if "--esik" in a else 8.0
    yollar = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] != "--esik")]
    if not yollar: print(__doc__); return 0
    sonuc = []
    for y in yollar:
        r = oku(y)
        if r is None or "ortalama" not in r: print(f"ÖZET satırı yok: {y}"); return 1
        sonuc.append(r); print(f"{y}: ORTALAMA {r['ortalama']:.2f} · KRITIK {int(r.get('kritik', 0))}")
    ort = sum(r["ortalama"] for r in sonuc) / len(sonuc); kritik = sum(int(r.get("kritik", 0)) for r in sonuc)
    gecti = ort >= esik and kritik == 0
    print(f"GENEL: {ort:.2f} / eşik {esik} · KRITIK {kritik} → {'GEÇTİ' if gecti else 'GEÇMEDİ'}")
    return 0 if gecti else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
