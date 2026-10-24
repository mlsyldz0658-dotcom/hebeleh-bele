"""BÜYÜT — 720p'den yayın görüntüsüne: yalnız kullanılan pencereler 2× büyütülür (TASARIM D-29, §6.5 `buyut.py`).

Kullanım:
  python buyut.py --film <film> [--plan 121,122] [--saglayici sahte] [--pay 0.5]
    → KURGU/surumler/v<N>/buyuk/NNN.mp4 + buyuk/BUYUTME.json {planlar: {no: {motor, ofset, yuz}}, dort_k_uygun}
Zincir (§5.6 buyutme): yz_buyutucu (Real-ESRGAN türü, ayrı CUDA ortamı, KUR3) → lanczos (+ ince gren) → sahte (testte Lanczos).
  - Pencere: kullanim ± pay (vars. 0,5 sn; kurgucunun küçük kırpma payı). ofset = pencere başı; capcut_taslak kaynak aralığını buna göre kaydırır.
  - Yüz denetimi: yapay zekâ büyütücüsünden sonra yüz bölgesinde SFace yeniden ölçülür (olcum paketi); 0,363 altı HATA → o plan Lanczos'a düşer.
    Ölçülemezse ÖLÇÜLEMEDİ (= BAYRAK) ve "4K" yazılamaz (dort_k_uygun false; yayin-paketcisi başlıkta "4K"yı ancak kapı geçerse yazar).
  - Süre koruması: Ö0-c'de ölçülen büyütme hızıyla 1 saatlik içerik > 12 saat sürecekse doğrudan 1080p Lanczos + gren yolu.
Çıkış kodları: 0 tamam · 1 hata · 2 KURGU_PLANI yok · 4 ffmpeg/sağlayıcı yok.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak, kurgu_ortak as ko

SURUM = "buyut 1.0"
SFACE_ESIK = 0.363
SURE_TAVAN_ORAN = 12.0          # 1 saatlik içerik için 12 saat (D-29; tahmin)


def yuz_denetle(once, sonra, t):
    """SFace benzerliği (büyütme öncesi ↔ sonrası aynı kare). olcum paketi yoksa None (ÖLÇÜLEMEDİ)."""
    try:
        from olcum import kimlik                                  # YuNet + SFace (adım 12)
        if not kimlik.hazir()[0]: return None
        a, b = ko.kare_rgb(once, t, 1280, 720), ko.kare_rgb(sonra, t, 1280, 720)
        if a is None or b is None: return None
        fa, fb = kimlik.yuzler(np.ascontiguousarray(a[:, :, ::-1])), kimlik.yuzler(np.ascontiguousarray(b[:, :, ::-1]))
        if not fa or not fb: return None
        en = lambda fs: max(fs, key=lambda f: f["kutu"][2] * f["kutu"][3])
        return float(kimlik.benzerlik(np.asarray(en(fa)["vektor"]), np.asarray(en(fb)["vektor"])))
    except Exception: return None


def hiz_orani():
    try: o = ortak.json_oku(os.path.join(ortak.yollar()["veri_kok"], "BILGI", "OLCUM0", "O0c.json"), {}) or {}
    except ortak.YolYok: return None
    return (o.get("buyutme") or {}).get("sn_basina_sn")


def buyut(kok, argv=()):
    argv = list(argv); kp_yol, kp = ko.kurgu_plani(kok)
    if not kp: return 2, None
    if not ko.ffmpeg_var(): print("!! ffmpeg yok", flush=True); return 4, None
    sec = ko.secenek(argv, "--plan"); nolar = {int(x) for x in sec.split(",")} if sec else None; pay = float(ko.secenek(argv, "--pay", 0.5))
    n = int(kp.get("kurgu_surumu") or 1); hedef = os.path.join(kok, "KURGU", "surumler", f"v{n}", "buyuk"); os.makedirs(hedef, exist_ok=True)
    gecici = os.path.join(hedef, "_pencere"); os.makedirs(gecici, exist_ok=True)
    ps = [x for x in kp.get("planlar") or [] if x["goruntu"].get("tur") == "video" and (not nolar or x["plan"] in nolar)]
    toplam = sum(float(x["sure"]) for x in ps); oran = hiz_orani()
    yz_kapali = bool(oran and oran * 3600.0 > SURE_TAVAN_ORAN * 3600.0)
    zin = [s for s in ko.zincir("buyutme", argv) if not (yz_kapali and getattr(s, "ad", "") == "yz_buyutucu")]
    if not zin: print("!! büyütme sağlayıcısı yok (ffmpeg?)", flush=True); return 4, None
    from saglayicilar import Kisitlandi
    kayit = {"_uretim": ko.po.zarf("A16", SURUM), "kurgu_plani_surumu": n, "pay_sn": pay, "yz_kapali_sure": yz_kapali,
             "toplam_kullanilan_sn": round(toplam, 2), "planlar": {}}
    for x in ps:
        u = x["goruntu"]["kullanim"]; klip = ko.mutlak(kok, x["goruntu"]["dosya"])
        ofset = max(0.0, u["bas"] - pay); sure = u["sure"] + (u["bas"] - ofset) + pay
        pen = os.path.join(gecici, f"{int(x['plan']):03d}.mp4")
        ko.ffmpeg("-ss", f"{ofset:.3f}", "-i", klip, "-t", f"{sure:.3f}", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "12",
                  "-pix_fmt", "yuv420p", "-c:a", "aac", pen)
        cikti = os.path.join(hedef, f"{int(x['plan']):03d}.mp4"); sonuc, motor, yuz = None, None, "olculemedi"
        for s in zin:
            try: sonuc = s.buyut(kok, pen, cikti, 2); motor = s.ad
            except Kisitlandi as e:
                if not e.gecilebilir: raise
                continue
            if sonuc.get("yz"):
                v = yuz_denetle(pen, cikti, min(sure / 2, u["bas"] - ofset + u["sure"] / 2))
                if v is None: yuz = "olculemedi"
                elif v < SFACE_ESIK: yuz = round(v, 3); sonuc = None; continue      # büyütücü yüzü değiştirdi → sıradaki (Lanczos)
                else: yuz = round(v, 3)
            else: yuz = "gerekmez"
            break
        if sonuc is None: print(f"!! #{x['plan']} büyütülemedi", flush=True); return 1, None
        kayit["planlar"][str(x["plan"])] = {"motor": motor, "yz": bool(sonuc.get("yz")), "ofset": round(ofset, 3), "yuz": yuz,
                                            "dosya": ko.goreli(kok, cikti)}
    kayit["dort_k_uygun"] = bool(kayit["planlar"]) and all(v["yz"] and isinstance(v["yuz"], float) and v["yuz"] >= SFACE_ESIK
                                                           for v in kayit["planlar"].values())
    ortak.atomik_yaz(os.path.join(hedef, "BUYUTME.json"), kayit)
    print(f"büyütme: {len(kayit['planlar'])} plan · 4K uygun: {'evet' if kayit['dort_k_uygun'] else 'hayır'}", flush=True)
    return 0, kayit


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    k, _ = buyut(kok, argv)
    if k == 2: print("!! KURGU_PLANI yok", flush=True)
    return k


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
