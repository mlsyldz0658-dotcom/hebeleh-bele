"""MEMMET TOPLA — Flow'a gönderilmiş ama indirilmemiş işleri YENİ GÖNDERİM YAPMADAN toplar (TASARIM §6.1, D-02; UM2 §4.2.1, S5).

Kullanım:
  python memmet_topla.py <film_klasoru> [--gorev <görev_id>] [--film <film>] [--kuru]
        KREDI_DEFTERI.jsonl'daki gönderim satırlarını MEMMET_DURUM.json işleri ve KUNYE/ ile eşler; açık kalanları Flow projesinde
        istem metniyle arar: hazırsa indirir (SIRALI_VIDEO/NNN.mp4 + KUNYE/NNN.json), sürüyorsa bırakır, bulunamazsa "kayip" yazar
        (kayıp iş kuyruktan, bütçe noktasından geçerek BİR kez yeniden gönderilir; bu araç göndermez). Biten blokların işaretini yazar.
        "Kayıp" yalnız sanal liste baştan sona kaydırılıp kart hiç bulunamadıysa; kart var ama sonuç yoksa iş SÜRÜYOR sayılır (8).
  --kuru: Flow'u açmadan yalnız açık işleri listeler.
Kurallar:
  - Hiçbir zaman istem yazmaz, GÖNDER'e basmaz, sayfayı yenilemez. Flow uyarısı → her durumda anında dur, kilit, 7 (uyarının yol açtığı
    beklenmeyen hatada da). Sayfadaki her işlem (gezinme, kaydırma, üstüne gelme) memmet.Memmet.dokun kapısından geçer.
  - FLOW_KILIDI varken açılmaz (7): uyarıdan sonraki toplama, kilit UYARI_GECTI.bat ile kalktıktan sonradır.
  - Doğrulama / oturum düşmesi → beklemez, 2. Aynı hesapta başka Memmet açıksa 8.
Çıkış kodları: 0 açık iş kalmadı · 2 durdu (doğrulama/giriş) · 7 Flow uyarısı/kilit · 8 hâlâ süren iş var ya da başka Memmet açık.
"""
import os, sys, json, time
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import memmet, blok_plani
from memmet import Durdur

SURUM = "memmet_topla 1.0"


def proje_ac(m):
    """Yalnız kayıtlı projeye gider (yeni proje AÇMAZ, yazmaz). Proje yoksa False."""
    if not m.D.get("proje_url"): return False
    m.dokun(m.page.goto, m.D["proje_url"], wait_until="commit")
    m.bekle_ogeyi(".ProseMirror", 45); m.bekle(2, 4)
    m.kontrol_noktasi(); m.yukari()
    return True


KAYDIR_JS = """() => { const k = document.getElementById('main-content') || document.scrollingElement;
    const once = k.scrollTop; k.scrollBy(0, Math.max(400, k.clientHeight * 0.8));
    return {son: k.scrollTop === once || k.scrollTop + k.clientHeight >= k.scrollHeight - 2}; }"""
KAYDIR_MAX = 60


def kutu_ara(m, istem):
    """Sanal listede kartı arar: görünmüyorsa liste sonuna kadar kaydırır (dokun), her adımda okur; sonunda başa döner."""
    r = m.kutu_bul(istem)
    if r.get("var"): return r
    try:
        for _ in range(KAYDIR_MAX):
            d = m.dokun(m.page.evaluate, KAYDIR_JS)
            m.bekle(0.8, 1.2)
            r = m.kutu_bul(istem)
            if r.get("var") or not isinstance(d, dict) or d.get("son", True): break
        if not r.get("var"): r = m.kutu_bul(istem)
    finally:
        m.yukari()
    return r


def _is(k, d, m):
    p = m.planlar.get(int(d["plan"] or 0)) or {}
    return {"plan": int(d["plan"] or 0), "tur": d.get("tur") or "video", "istem": d.get("istem") or "", "is": k, "yedek": False,
            "deneme": (m.D["isler"].get(k) or {}).get("deneme"), "model": (p.get("uretim") or {}).get("model") or "omni-1.1-flash",
            "cozunurluk": m.A["video_cozunurluk"], "dosyalar": [], "madde": k, "dilim": "ana", "kredi": 0}


def topla(root, sayfa=None, kuru=False):
    """(çıkış kodu, özet). sayfa: testlerde sahte Flow sayfası."""
    m = memmet.Memmet(root, {"mod": "elle", "topla": True})
    m.planlar = {int(p["no"]): p for p in m.plan.get("sahneler") or [] if isinstance(p.get("no"), (int, float))}
    acik = blok_plani.acik_gonderimler(m.root, m.D["isler"])
    ozet = {"acik": len(acik), "indirilen": [], "suren": [], "kayip": [], "reddedilen": [], "hata": []}
    m.ozet = {"indirilen": [], "atlanan": [], "reddedilen": [], "hata": [], "zaman_asimi": [], "gonderilen": [], "dur": False}
    if not acik or kuru: return 0, dict(ozet, isler=acik if kuru else {})
    m.on_kosullar()                                     # FLOW_KILIDI → 7, sayfa açılmaz
    memmet.flow_kilidi_al(m.film)
    try:
        if sayfa is None: m.chrome_ac()
        else: m.page = sayfa
        m.giris_kontrol(); m.hesap_denetle()
        if not proje_ac(m):
            for k, d in acik.items(): _kayip(m, k, d, ozet, "Flow projesi kaydı yok")
            return _bitir(m, acik, ozet)
        for k, d in acik.items():
            m.kontrol_noktasi()
            if not d.get("istem"): _kayip(m, k, d, ozet, "istem metni kaydı yok (eşlenemez)"); continue
            m.D["isler"].setdefault(k, {"plan": d["plan"], "tur": d["tur"], "istem": d["istem"], "durum": d["durum"], "blok": d.get("blok")})
            m.blok_id = d.get("blok") or m.D["isler"][k].get("blok")
            r = kutu_ara(m, d["istem"])
            if r.get("var"): m.olagandisi_denetle(r.get("metin", ""))
            if not r.get("var"): _kayip(m, k, d, ozet, "Flow projesinde bulunamadı (liste sonuna kadar kaydırıldı)"); continue
            if r.get("yuzde"): ozet["suren"].append(d["plan"]); continue
            hazir = r.get("video_kutusu") if d["tur"] == "video" else r.get("gorsel_url")
            if hazir:
                try:
                    if m.indir_v2({"j": _is(k, d, m), "istem": d["istem"], "t": time.time()}, r): ozet["indirilen"].append(d["plan"]); continue
                except Exception as e: m.log(f"{d['plan']:03d} indirilemedi: {str(e)[:80]}")
                ozet["suren"].append(d["plan"]); continue
            durum = "filtre_red" if m.red_mi(r, memmet.FILTRE_KELIMELERI) else ("hata" if m.red_mi(r, memmet.HATA_KELIMELERI) else None)
            if durum:
                m.D["isler"][k]["durum"] = durum; m.save(); ozet["reddedilen" if durum == "filtre_red" else "hata"].append(d["plan"])
            else: ozet["suren"].append(d["plan"])          # kart var, sonuç ve açık hata yok: iş sürüyor (kayıp DEĞİL)
        m.son_denetim()
        return _bitir(m, acik, ozet)
    except Exception:
        u = memmet.uyari_var_mi(m)          # beklenmeyen hata uyarının kendisinden olabilir: önce salt okunur
        if u: raise Durdur(u, kod="olagandisi")
        raise
    finally:
        m.kapat(); memmet.flow_kilidi_birak()


def _kayip(m, k, d, ozet, neden):
    m.D["isler"].setdefault(k, {"plan": d["plan"], "tur": d["tur"], "istem": d.get("istem"), "blok": d.get("blok")})
    m.D["isler"][k].update(durum="kayip", kayip_neden=neden, kayip_zaman=time.strftime("%Y-%m-%d %H:%M:%S")); m.save()
    ozet["kayip"].append(d["plan"]); m.log(f"{d['plan']:03d}: kayıp ({neden}); yeniden gönderim kuyruktan ve bütçe noktasından, bir kez")


def _bitir(m, acik, ozet):
    kalan = blok_plani.acik_gonderimler(m.root, m.D["isler"])
    for b in sorted({d.get("blok") for d in acik.values() if d.get("blok")}):
        if not any(v.get("blok") == b for v in kalan.values()) and not blok_plani.blok_bitti_mi(m.root, b):
            blok_plani.bitti_isaretle(m.root, b, {"toplandi": True})
    ozet["kalan"] = len(kalan)
    memmet._atomik(os.path.join(m.root, "_memmet_topla.json"), dict(ozet, zaman=time.strftime("%Y-%m-%d %H:%M:%S"), arac=SURUM))
    m.log(f"TOPLA: {len(ozet['indirilen'])} indirildi, {len(ozet['suren'])} sürüyor, {len(ozet['kayip'])} kayıp")
    return (8 if kalan else 0), ozet


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    root = argv[argv.index("--film") + 1] if "--film" in argv else next((a for a in argv if not a.startswith("--")), None)
    if "--gorev" in argv and argv.index("--gorev") + 1 < len(argv) and argv[argv.index("--gorev") + 1] == root: root = None
    if not root or not os.path.isdir(root): print("film klasörü yok"); return 4
    try:
        kod, ozet = topla(root, kuru="--kuru" in argv)
        print(json.dumps(ozet, ensure_ascii=False)); return kod
    except Durdur as e:
        return memmet.bitir(None, root, e.kod, str(e))
    except Exception as e:
        print("!! beklenmeyen hata:", str(e)[:200]); memmet.cikis_yaz(root, "beklenmeyen", "memmet_topla beklenmeyen hata"); return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
