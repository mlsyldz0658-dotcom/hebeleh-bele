"""FİKSTÜR DENETİMİ — Ö0-b istem fikstürünün (O0b_istemler_v<N>.json) şema ve güvenlik denetimi (TASARIM §1.2 Ö0-b, D-04, D-13, §10.4).

Kullanım:
  python fikstur_denetim.py [<fikstur.json>] [--b3-kok <B3 klasörü>] [--json]
        Dosya verilmezse sırayla: ARACLAR/olcum0/fikstur/O0b_istemler_v1.json → <veri>/GELISTIRME/olcum0/fikstur/O0b_istemler_v1.json.
        --b3-kok verilirse her "kare" dosyasının varlığı ve SHA1'i (kare_sha1 öneki) da denetlenir.
Kodda: import fikstur_denetim as fd; bulgular = fd.denetle(doc, b3_kok=None); fd.hata_var(bulgular); fd.gun_dagilimi(doc, tavanlar)
Şema: O0b_istemler_sema.json (aynı klasör). Şablon: O0b_istemler_SABLON.json ("sablon": true; gerçek ölçümde KULLANILAMAZ).
HATA (fikstür kullanılamaz): şema alanı eksik/yanlış · kimlik tekrarı · gerçek fikstürde istem sayısı 45 değil (şablonda ≤ 45) ·
  filtre/yaş/risk kelimesi (istem_denetim listeleri; politika reddini kasıtlı tetikleyebilecek istem yasak, §10.4) · biçim kolu ile istem
  metni uyuşmuyor (aralik: "0.5-3s:" kalıbı şart; sira: aralık kalıbı yasak) · bekleme kolu istemde birebir yok · adım saatleri D-13 dışında
  (ilk ≥ 0,5 sn; son ≤ klip_sn − 1,0; klip başına 2–3 adım) · gun alanı yok ya da gün dolu (gün N ≤ o0b_gun_tavanlari[N−1];
  gerçek fikstürde tam o kadar) · zincir kaynağı yok, sonra geliyor ya da aynı/sonraki merdiven gününde · zincir kare
  saniyesi pencere dışında (≤ klip_sn − 0,5) · B3 karesi yok / SHA1 tutmuyor (--b3-kok ile) · b3_denetim "iki_tur_gecti" değil.
BAYRAK (kullanılır, bilgi): bir A/B kolunda < ab_kol_min_ornek (12) istem → o A/B "ölçülemedi → varsayılan" olacak (TASARIM §1.2).
Çıkış kodları: 0 HATA yok · 1 HATA var · 2 dosya yok · 4 kullanım.
"""
import os, re, sys, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); OLCUM0 = os.path.dirname(HERE); ARACLAR = os.path.dirname(OLCUM0)
for _p in (ARACLAR, OLCUM0):
    if _p not in sys.path: sys.path.insert(0, _p)
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SURUM = "fikstur_denetim 1.0"
GERCEK_SAYI = 45
KIMLIK = re.compile(r"O0B-\d{3}")
ARALIK = re.compile(r"\b\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?\s*s\s*:")
BICIMLER = ("aralik", "sira")
BEKLEMELER = ("holds still", "holds the pose, breathing")
ZINCIR_KARE = ("dogal_1280x720", "1376x774_kirp3")
DENEYLER = ("ab", "zincir")
TAVANLAR_VARSAYILAN = [10, 15, 20]
AB_MIN_VARSAYILAN = 12


def _sha1(yol):
    h = hashlib.sha1()
    with open(yol, "rb") as f:
        for p in iter(lambda: f.read(1 << 20), b""): h.update(p)
    return h.hexdigest()


def _filtre_listeleri():
    try:
        import istem_denetim as idn
        return list(idn.FILTRE_KELIMELERI) + list(idn.RISK_KELIMELERI), idn.YAS_IFADESI
    except Exception:                                   # istem_denetim yoksa eşdeğer en dar liste
        return (["girl", "little", "child", "children", "kid", "kids", "baby", "toddler", "siblings", "frail", "bed", "sleep",
                 "sleeping", "cheek", "chest", "trembles", "trembling", "blood", "bloody", "corpse", "dead body", "kill", "killed", "stab",
                 "gore", "wound"],
                re.compile(r"\b\d+\s*(?:-\s*)?(?:years?|yrs?)(?:\s*-\s*|\s+)old\b|\byear-old\b|\byoung\b", re.I))


def filtre_tara(metin):
    """İstemde filtre/risk kelimesi ya da yaş ifadesi: bulunanlar listesi (boş = temiz)."""
    kel, yas = _filtre_listeleri(); m = (metin or "").lower(); out = []
    for k in kel:
        if re.search(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])", m): out.append(k)
    if yas.search(metin or ""): out.append("yaş ifadesi")
    return out


def esikler_al():
    try:
        import esikler
        E = esikler.yukle()
        return list(E.get("o0b_gun_tavanlari") or TAVANLAR_VARSAYILAN), int(E.get("ab_kol_min_ornek") or AB_MIN_VARSAYILAN)
    except Exception: return list(TAVANLAR_VARSAYILAN), AB_MIN_VARSAYILAN


def gun_dagilimi(doc, tavanlar=None):
    """{istem_id: merdiven günü} — her istemin "gun" alanı (1..len(tavanlar)). Gün N'nin istemleri yalnız merdivenin N. basamağında
    (o0b_gun_tavanlari[N-1]) gönderilir; basamak tam ve uyarısız bitmeden N+1'e geçilmez."""
    return {it.get("id"): it.get("gun") for it in (doc.get("istemler") or []) if isinstance(it, dict)}


def _b(seviye, madde, neden, kimlik=None):
    d = {"seviye": seviye, "madde": madde, "neden": neden}
    if kimlik: d["id"] = kimlik
    return d


def denetle(doc, b3_kok=None, tavanlar=None, ab_min=None):
    """Bulgu listesi. HATA'sız fikstür ölçümde kullanılabilir."""
    t0, m0 = esikler_al(); tavanlar = tavanlar or t0; ab_min = ab_min or m0
    B = []
    if not isinstance(doc, dict): return [_b("HATA", "sema", "üst düzey sözlük değil")]
    if doc.get("_sema") != "O0b_istemler": B.append(_b("HATA", "sema", "_sema 'O0b_istemler' değil"))
    if not re.fullmatch(r"v\d+", str(doc.get("fikstur_surum") or "")): B.append(_b("HATA", "sema", "fikstur_surum 'v<N>' değil"))
    sablon = doc.get("sablon")
    if not isinstance(sablon, bool): B.append(_b("HATA", "sema", "sablon true|false olmalı"))
    ist = doc.get("istemler")
    if not isinstance(ist, list) or not ist: return B + [_b("HATA", "sema", "istemler boş ya da liste değil")]
    if sablon is False and len(ist) != GERCEK_SAYI: B.append(_b("HATA", "sayi", f"gerçek fikstürde {GERCEK_SAYI} istem olmalı ({len(ist)})"))
    if len(ist) > GERCEK_SAYI: B.append(_b("HATA", "sayi", f"en çok {GERCEK_SAYI} istem (Ö0-b üst sınırı; {len(ist)})"))
    gun = gun_dagilimi(doc, tavanlar); sira = {}; gorulen = set()
    for i, it in enumerate(ist):
        k = it.get("id") if isinstance(it, dict) else None
        if not isinstance(it, dict) or not isinstance(k, str) or not KIMLIK.fullmatch(k):
            B.append(_b("HATA", "kimlik", f"{i + 1}. istemin id'si O0B-NNN değil")); continue
        if k in gorulen: B.append(_b("HATA", "kimlik", "kimlik tekrarı", k))
        gorulen.add(k); sira[k] = i
        dn = it.get("deney"); kol = it.get("kollar") or {}
        g = it.get("gun")
        if not isinstance(g, int) or isinstance(g, bool) or not 1 <= g <= len(tavanlar):
            B.append(_b("HATA", "gun", f"gun 1..{len(tavanlar)} tamsayı olmalı (merdiven basamağı)", k))
        if dn not in DENEYLER: B.append(_b("HATA", "deney", f"deney {DENEYLER} olmalı", k)); continue
        if kol.get("istem_bicimi") not in BICIMLER: B.append(_b("HATA", "kol", "kollar.istem_bicimi aralik|sira", k))
        if kol.get("bekleme") not in BEKLEMELER: B.append(_b("HATA", "kol", f"kollar.bekleme {BEKLEMELER}", k))
        metin = it.get("istem")
        if not isinstance(metin, str) or len(metin.split()) < 8: B.append(_b("HATA", "istem", "istem metni yok ya da çok kısa", k)); continue
        f = filtre_tara(metin)
        if f: B.append(_b("HATA", "filtre", "filtre/risk kelimesi: " + ", ".join(f) + " (kasıtlı tetikleme riski; §10.4)", k))
        if kol.get("istem_bicimi") == "aralik" and not ARALIK.search(metin):
            B.append(_b("HATA", "bicim", "aralik kolunda '0.5-3s:' kalıbı yok", k))
        if kol.get("istem_bicimi") == "sira" and ARALIK.search(metin):
            B.append(_b("HATA", "bicim", "sira kolunda aralık kalıbı var", k))
        if kol.get("bekleme") in BEKLEMELER and kol["bekleme"] not in metin:
            B.append(_b("HATA", "bekleme", f"istemde '{kol['bekleme']}' birebir yok", k))
        ksn = it.get("klip_sn", 8)
        if ksn != 8: B.append(_b("HATA", "klip_sn", "Ö0-b 720p 8 sn ölçer (klip_sn 8)", k))
        ad = it.get("adimlar")
        if not isinstance(ad, list) or not 2 <= len(ad) <= 3: B.append(_b("HATA", "adim", "klip başına 2–3 adım (D-13)", k))
        else:
            try:
                bas = [float(a["bas"]) for a in ad]; bit = [float(a["bit"]) for a in ad]
                if bas[0] < 0.5: B.append(_b("HATA", "adim", "ilk adım ≥ 0,5 sn'de başlar", k))
                if bit[-1] > ksn - 1.0 + 1e-9: B.append(_b("HATA", "adim", "son adım klip_sn − 1,0'da biter", k))
                if any(b1 > b0 + 1e-9 for b0, b1 in zip(bas[1:], bit[:-1])) or any(x >= y for x, y in zip(bas, bit)):
                    B.append(_b("HATA", "adim", "adımlar sıralı ve çakışmasız olmalı", k))
                if any(not str(a.get("metin") or "").strip() for a in ad): B.append(_b("HATA", "adim", "adım metni boş", k))
            except (KeyError, TypeError, ValueError): B.append(_b("HATA", "adim", "adımda bas/bit sayı değil", k))
        z = it.get("zincir") or {}
        if dn == "ab":
            if kol.get("son_kare_ref", "yok") != "yok" or kol.get("zincir_kare") is not None:
                B.append(_b("HATA", "kol", "ab deneyinde son_kare_ref 'yok', zincir_kare null", k))
            if z: B.append(_b("HATA", "zincir", "ab deneyinde zincir alanı olmaz", k))
        else:
            ref = kol.get("son_kare_ref")
            if ref not in ("var", "yok"): B.append(_b("HATA", "kol", "zincir deneyinde son_kare_ref var|yok", k))
            if ref == "var" and kol.get("zincir_kare") not in ZINCIR_KARE: B.append(_b("HATA", "kol", f"zincir_kare {ZINCIR_KARE}", k))
            if ref == "yok" and kol.get("zincir_kare") is not None: B.append(_b("HATA", "kol", "son_kare_ref yok iken zincir_kare null", k))
            kay = z.get("kaynak")
            if kay not in sira: B.append(_b("HATA", "zincir", f"zincir.kaynak {kay!r} daha önce gelen bir istem değil", k))
            else:
                kit = ist[sira[kay]]
                if kit.get("deney") != "ab": B.append(_b("HATA", "zincir", "zincir kaynağı ab deneyi olmalı (derinlik 1)", k))
                if (gun.get(kay) or 0) >= (gun.get(k) or 99): B.append(_b("HATA", "zincir", "zincir kaynağı daha önceki bir merdiven gününde olmalı", k))
                if ref == "var":
                    try:
                        ks = float(z.get("kare_sn"))
                        son = max(float(a["bit"]) for a in kit.get("adimlar") or [{"bit": 0}])
                        if not (son + 0.2 - 1e-9 <= ks <= 8 - 0.5 + 1e-9):
                            B.append(_b("HATA", "zincir", f"kare_sn {ks} pencere dışında [{son + 0.2:.2f}, 7.5] (D-15, Y55)", k))
                    except (TypeError, ValueError): B.append(_b("HATA", "zincir", "kare_sn sayı değil", k))
        kare_gerek = dn == "ab" or kol.get("son_kare_ref") == "yok" or bool(it.get("kare"))   # zincir/var: kare = G1Z için planlı B3 karesi
        if kare_gerek:
            if not it.get("kare") or not re.fullmatch(r"[0-9a-f]{8,40}", str(it.get("kare_sha1") or "")):
                B.append(_b("HATA", "kare", "kare (B3 kök klasörüne göre yol) ve kare_sha1 (≥ 8 hane küçük hex) şart", k))
            elif b3_kok:
                p = os.path.join(b3_kok, str(it["kare"]))
                if not os.path.isfile(p): B.append(_b("HATA", "kare", f"B3 karesi yok: {it['kare']}", k))
                elif not _sha1(p).startswith(str(it["kare_sha1"])): B.append(_b("HATA", "kare", "B3 karesinin SHA1'i tutmuyor", k))
            if it.get("b3_denetim") != "iki_tur_gecti": B.append(_b("HATA", "kare", "b3_denetim 'iki_tur_gecti' olmalı (yalnız denetimden geçmiş P1 kareleri)", k))
    # gün dolulukları: gün N ≤ tavan N; gerçek fikstürde gün N = tavan N (10/15/20 = 45)
    for n, t in enumerate(tavanlar, 1):
        c = sum(1 for x in ist if isinstance(x, dict) and x.get("gun") == n)
        if c > t: B.append(_b("HATA", "gun", f"gün {n}: {c} istem > tavan {t}"))
        elif sablon is False and c != t: B.append(_b("HATA", "gun", f"gün {n}: {c} istem; gerçek fikstürde tavan kadar ({t}) olmalı"))
    if sablon is False and sum(tavanlar) != GERCEK_SAYI:
        B.append(_b("BAYRAK", "gun", f"merdiven toplamı {sum(tavanlar)} ≠ {GERCEK_SAYI}"))
    # A/B kol sayıları (bilgi)
    ab = [x for x in ist if isinstance(x, dict) and x.get("deney") == "ab"]
    zn = [x for x in ist if isinstance(x, dict) and x.get("deney") == "zincir"]
    for etk, liste, deg in (("istem_bicimi", ab, BICIMLER), ("bekleme", ab, BEKLEMELER), ("son_kare_ref", zn, ("var", "yok")),
                            ("zincir_kare", [x for x in zn if (x.get("kollar") or {}).get("son_kare_ref") == "var"], ZINCIR_KARE)):
        say = {d: sum(1 for x in liste if (x.get("kollar") or {}).get(etk) == d) for d in deg}
        if min(say.values()) < ab_min:
            B.append(_b("BAYRAK", "kol_sayisi", f"{etk}: {say} — kol başına < {ab_min} → bu A/B 'ölçülemedi → varsayılan' olur"))
    return B


def hata_var(B): return any(b["seviye"] == "HATA" for b in B)


def varsayilan_yol():
    """(yol, kaynak) — depo kopyası önce, yoksa <veri>/GELISTIRME kopyası; ikisi de yoksa (None, None)."""
    d = os.path.join(HERE, "O0b_istemler_v1.json")
    if os.path.isfile(d): return d, "depo"
    try:
        import ortak
        g = os.path.join(ortak.yollar()["gelistirme"], "olcum0", "fikstur", "O0b_istemler_v1.json")
        if os.path.isfile(g): return g, "gelistirme"
    except Exception: pass
    return None, None


def oku(yol):
    with open(yol, encoding="utf-8-sig") as f: return json.load(f)


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    b3 = None; dosya = None; i = 0
    while i < len(argv):
        if argv[i] == "--b3-kok" and i + 1 < len(argv): b3 = argv[i + 1]; i += 2; continue
        if not argv[i].startswith("--"): dosya = argv[i]
        i += 1
    if not dosya: dosya, _ = varsayilan_yol()
    if not dosya or not os.path.isfile(dosya):
        print("Ö0-b fikstürü yok (O0b_istemler_v1.json). Nasıl yazılır: olcum0/BENIOKU.md."); return 2
    try: doc = oku(dosya)
    except ValueError as e: print(f"fikstür JSON bozuk: {e}"); return 1
    B = denetle(doc, b3_kok=b3)
    if "--json" in argv: print(json.dumps({"dosya": dosya, "bulgular": B, "hata": hata_var(B)}, ensure_ascii=False, indent=1))
    else:
        print(f"{os.path.basename(dosya)}: {len(doc.get('istemler') or [])} istem · şablon: {doc.get('sablon')} · "
              f"HATA {sum(b['seviye'] == 'HATA' for b in B)} · BAYRAK {sum(b['seviye'] == 'BAYRAK' for b in B)}")
        for b in B: print(f"  {b['seviye']}: {b.get('id', '-')} {b['madde']} — {b['neden']}")
    return 1 if hata_var(B) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
