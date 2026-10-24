"""EVREN FİLM SONU — evren.py'nin A18 komutları: --film-sonu, --yedekle, --yedek-dogrula (TASARIM §1.3 A18/A00, §5.4, D-42, [SON] O-6).

evren.py bu komutları bu modüle yönlendirir (bağlantı satırı: paylaşılan istek); doğrudan da çağrılabilir:
  python evren_film_sonu.py --film-sonu --film <film>
        filmin sonucunu seri evrenine EKLER: evren.json filmler + film_sonu kaydı; hikaye.json kanon (yalnız eklenir), seri soruları
        (HIKAYE seri_kancasi.sonraki_tohum açık soru olur), başlık geçmişi (YAYIN/PAKET.json); karakterlerin hikaye.json'u (yay geçmişi,
        durum: yasiyor → olu olabilir, olu → yasiyor HATA), DURUM_SON.json (DUNYA_DEFTERI'nin son durumu; sonraki filmin başlangıcı),
        sablonlar/jenerik.json (filmde kullanılan jenerik şablonu evrende yoksa). Kaynak: _HIKAYE_ODASI/EVREN_TASLAK.json
        (hikaye-yazari·evren) + HIKAYE.json + YAYIN/PAKET.json. Aynı film için yeniden çalıştırmak bir şey değiştirmez.
  python evren_film_sonu.py --yedekle (--film <film> | --seri SERI) [--hedef <yedek kökü>] [--yalniz-evren]
        <evren>/<SERI> → <yedek>/EVREN/<SERI>/ KOPYA (robocopy /E; /MIR yok) + SHA1_LISTESI.json. --film verildiğinde (A18 görevi)
        ders defteri de yedeklenir (ders_defteri --yedekle ile aynı iş; --yalniz-evren kapatır). D takılı değilse bilgi, çıkış 0.
  python evren_film_sonu.py --yedek-dogrula (--film <film> | --seri SERI) [--yenile]
        A00: yedeğin sha1 listesi şimdiki evrenle karşılaştırılır; fark bilgi olarak yazılır, --yenile ile yedek yenilenir.
Kodda: film_sonu(film) → (rapor, kod) · yedekle(seri, hedef_kok=None, dersler=False) → rapor · yedek_dogrula(seri, ...) → rapor
Kurallar: <evren>/ altına yalnız evren.py ailesi yazar; hiçbir dosya silinmez (değişen dosyanın eski hâli <ad>_v<n>.json kalır);
kanon yalnız eklenir (taslak var olan kanon maddesini düşürürse HATA, hiçbir şey yazılmaz). AYARLAR yedeğe girmez.
Çıkış kodları: 0 tamam (yedek ertelendiyse de) · 1 HATA (kanon ihlali, evren yok, sha1 uyuşmazlığı) · 4 ORTAM (YOLLAR.json yok).
"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, evren, ders_yedekle as dy

SURUM = "evren_film_sonu 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
KOMUTLAR = ("--film-sonu", "--yedekle", "--yedek-dogrula")


def _oku(p, v=None): return ortak.json_oku(p, v)


def _kopya(x): return json.loads(json.dumps(x))


def film_adi(film): return (_oku(os.path.join(film, "HAZIRLIK.json"), {}) or {}).get("film") or os.path.basename(os.path.abspath(film))


def _kanon_metni(k): return (k.get("olgu") or k.get("metin") or json.dumps(k, ensure_ascii=False, sort_keys=True)) if isinstance(k, dict) else str(k)


def _son_durum(film):
    d = _oku(os.path.join(film, "DUNYA_DEFTERI.json"))
    if not isinstance(d, dict): return None
    for a in ("son_durum", "bitis_durumu", "durum_son"):
        if d.get(a): return d[a]
    for a in ("durumlar", "kayitlar", "planlar"):
        v = d.get(a)
        if isinstance(v, list) and v: return v[-1]
        if isinstance(v, dict) and v: return v[sorted(v, key=lambda k: (len(str(k)), str(k)))[-1]]
    return None


def film_sonu(film):
    """(rapor, kod). Önce bütün değişiklikler hesaplanır, ihlal varsa hiçbir dosya yazılmaz."""
    film = os.path.abspath(film)
    h = evren.film_hikaye(film)
    if not isinstance(h, dict): return {"sonuc": "HATA", "hatalar": ["HIKAYE.json yok ya da bozuk"]}, HATA
    seri = evren.film_serisi(film, h)
    if not seri or not os.path.isfile(evren.seri_yolu(seri, "evren.json")):
        return {"sonuc": "HATA", "seri": seri, "hatalar": ["evrende bu seri yok (A06 ön kaydı yapılmamış: evren.py --on-kayit)"]}, HATA
    ad = film_adi(film)
    t = _oku(os.path.join(film, "_HIKAYE_ODASI", "EVREN_TASLAK.json"), {}) or {}
    paket = _oku(os.path.join(film, "YAYIN", "PAKET.json"), {}) or {}
    hatalar, yazilacak = [], []

    # evren.json
    e = _oku(evren.seri_yolu(seri, "evren.json"), {}) or {}; e2 = _kopya(e)
    baslik = (paket.get("baslik") if isinstance(paket.get("baslik"), str) else None) or ((h.get("baslik") or {}).get("secilen")
                                                                                     if isinstance(h.get("baslik"), dict) else None)
    kayit = {"baslik": baslik, "film_no": h.get("film_no"), "ozet": t.get("ozet") or h.get("logline"),
             "sonraki_tohum": t.get("sonraki_tohum") or (h.get("seri_kancasi") or {}).get("sonraki_tohum")}
    e2.setdefault("filmler", [])
    if ad not in e2["filmler"]: e2["filmler"].append(ad)
    onceki = {k: v for k, v in ((e2.get("film_sonu") or {}).get(ad) or {}).items() if k != "zaman"}
    if onceki != kayit: e2.setdefault("film_sonu", {})[ad] = dict(kayit, zaman=evren.simdi())
    if e2 != e:
        e2["surum"] = int(e.get("surum") or 0) + 1; e2["_uretim"] = {"arac_surum": SURUM, "zaman": evren.simdi()}
        yazilacak.append(("evren.json", e2))

    # hikaye.json: kanon yalnız eklenir
    hs = _oku(evren.seri_yolu(seri, "hikaye.json"), {}) or {}; hs2 = _kopya(hs)
    for a, v in (("kanon", []), ("seri_sorulari", []), ("baslik_gecmisi", []), ("degisiklik_gunlugu", [])): hs2.setdefault(a, v)
    var = [_kanon_metni(k) for k in hs2["kanon"]]
    if isinstance(t.get("kanon"), list):
        yeni_tam = {_kanon_metni(k) for k in t["kanon"]}
        dusen = [k for k in var if k not in yeni_tam]
        if dusen: hatalar.append(f"kanon yalnız eklenir; taslak {len(dusen)} kanon maddesini düşürüyor: {dusen[:3]}")
    for k in list(t.get("kanon_ekle") or []) + [x for x in (t.get("kanon") or []) if _kanon_metni(x) not in var]:
        m = _kanon_metni(k)
        if m not in var:
            hs2["kanon"].append(dict(k, film=ad) if isinstance(k, dict) else {"olgu": m, "film": ad}); var.append(m)
    sorular = hs2["seri_sorulari"]
    tohum = kayit["sonraki_tohum"]
    if tohum and not any(q.get("soru") == tohum for q in sorular):
        sorular.append({"id": f"sq{len(sorular) + 1:02d}", "soru": tohum, "durum": "acik", "acan_film": ad})
    for q in t.get("seri_sorulari") or []:
        if not isinstance(q, dict) or not q.get("soru"): continue
        es = next((x for x in sorular if x.get("soru") == q["soru"] or (q.get("id") and x.get("id") == q["id"])), None)
        if es is None: sorular.append(dict(q, durum=q.get("durum") or "acik", acan_film=ad))
        elif q.get("durum") == "kapandi" and es.get("durum") != "kapandi": es.update(durum="kapandi", kapatan_film=ad)
    if baslik and not any(b.get("film") == ad for b in hs2["baslik_gecmisi"]):
        hs2["baslik_gecmisi"].append({"film": ad, "baslik": baslik, "tarih": evren.simdi()[:10]})
    if hs2 != hs:
        hs2["surum"] = int(hs.get("surum") or 0) + 1
        hs2["degisiklik_gunlugu"].append({"surum": hs2["surum"], "tarih": evren.simdi()[:10], "film": ad, "ozet": "film sonu"})
        yazilacak.append(("hikaye.json", hs2))

    # karakterlerin hikâye dosyaları
    for kid, kt in (t.get("karakterler") or {}).items():
        if not isinstance(kt, dict) or not evren.KIMLIK_DESEN.fullmatch(str(kid)): continue
        rel = f"karakterler/{kid}/hikaye.json"; kh = _oku(evren.seri_yolu(seri, *rel.split("/")), {}) or {"id": kid, "durum": "yasiyor"}
        kh2 = _kopya(kh); kh2.setdefault("yay_gecmisi", []); kh2.setdefault("bildikleri", [])
        yeni_durum = kt.get("durum")
        if yeni_durum and yeni_durum != kh.get("durum"):
            if kh.get("durum") == "olu": hatalar.append(f"karakter '{kid}' evren kanonunda ölü; '{yeni_durum}' yapılamaz (kanon ihlali)")
            else: kh2["durum"] = yeni_durum
        if kt.get("yay") and not any(y.get("film") == ad for y in kh2["yay_gecmisi"]):
            kh2["yay_gecmisi"].append({"film": ad, "yay": kt["yay"]})
        for b in kt.get("bildikleri_ekle") or []:
            if b not in kh2["bildikleri"]: kh2["bildikleri"].append(b)
        if kh2 != kh: yazilacak.append((rel, kh2))

    # sonraki filmin başlangıcı
    sd = _son_durum(film)
    if sd is not None:
        ds = {"film": ad, "kaynak": "DUNYA_DEFTERI.json", "durum": sd}
        eski = _oku(evren.seri_yolu(seri, "DURUM_SON.json"))
        if not (isinstance(eski, dict) and {k: v for k, v in eski.items() if k != "zaman"} == ds):
            yazilacak.append(("DURUM_SON.json", dict(ds, zaman=evren.simdi())))

    # jenerik şablonu (kurgunun sonraki filmde yeniden kullandığı varlık)
    j = _oku(os.path.join(film, "YAYIN", "JENERIK", "jenerik.json"), {}) or {}
    if isinstance(j.get("sablon"), dict) and not os.path.exists(evren.seri_yolu(seri, "sablonlar", "jenerik.json")):
        yazilacak.append(("sablonlar/jenerik.json", dict(j["sablon"], ilk_film=ad)))

    if hatalar: return {"sonuc": "HATA", "seri": seri, "film": ad, "hatalar": hatalar, "degisen": []}, HATA
    degisen = []
    for rel, veri in yazilacak:
        if evren._surumlu_yaz(evren.seri_yolu(seri, *rel.split("/")), veri): degisen.append(rel)
    return {"sonuc": "GEC", "seri": seri, "film": ad, "degisen": degisen, "taslak": bool(t)}, BITTI


# --- yedek ---------------------------------------------------------------------------------------------------------
def evren_hedefi(seri, hedef_kok=None): return os.path.join(os.path.abspath(hedef_kok or ortak.yollar()["yedek"]), "EVREN", seri)


def yedekle(seri, hedef_kok=None, dersler=False):
    kaynak = evren.seri_yolu(seri)
    if not os.path.isdir(kaynak): return {"durum": "hata", "neden": f"evrende {seri} yok", "fark": []}
    r = dy.kopya_yedek(kaynak, evren_hedefi(seri, hedef_kok), kok=dy.yedek_koku(hedef_kok))
    dy.durum_yaz(f"evren/{seri}", r)
    out = {"evren": r}
    if dersler: out["dersler"] = dy.ders_yedekle(hedef_kok)
    out["durum"] = "hata" if any(x["durum"] == "hata" for x in out.values() if isinstance(x, dict)) else r["durum"]
    return out


def yedek_dogrula(seri, hedef_kok=None, yenile=False):
    r = dy.dogrula(evren.seri_yolu(seri), evren_hedefi(seri, hedef_kok), kok=dy.yedek_koku(hedef_kok))
    if yenile and r["durum"] in ("fark", "yedek_yok"): r["yenileme"] = yedekle(seri, hedef_kok)
    return r


# --- komut satırı ----------------------------------------------------------------------------------------------------
def _arg(a, ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v


def main(a):
    if not any(k in a for k in KOMUTLAR): print(__doc__); return ORTAM
    try:
        film = evren._film_yolu(_arg(a, "--film")); hedef = _arg(a, "--hedef")
        seri = evren.seri_normal(_arg(a, "--seri")) or (evren.film_serisi(film) if film else None)
        if "--film-sonu" in a:
            if not film: print("!! --film gerekli"); return HATA
            r, kod = film_sonu(film); print(json.dumps(r, ensure_ascii=False, indent=1)); return kod
        if not seri: print("!! seri bulunamadı (--seri ya da --film)"); return HATA
        if "--yedekle" in a:
            r = yedekle(seri, hedef, dersler=bool(film) and "--yalniz-evren" not in a)
            print(dy.mesaj(f"Evren {seri}", r["evren"]) if "evren" in r else f"!! {r.get('neden')}")
            if "dersler" in r: print(dy.mesaj("Ders defteri", r["dersler"]))
            return HATA if r["durum"] == "hata" else BITTI
        r = yedek_dogrula(seri, hedef, yenile="--yenile" in a)
        print(dy.mesaj(f"Evren {seri}", r)); [print("  -", x["dosya"], x["neden"]) for x in r["fark"][:20]]
        if "yenileme" in r: print(dy.mesaj(f"Evren {seri}", r["yenileme"].get("evren", r["yenileme"])))
        return BITTI
    except ortak.YolYok as e:
        print("!!", e); return ORTAM


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
