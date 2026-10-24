"""KÖR PAKET · İZLEME KİPLERİ — animatik, kurgu, kesit, kesici, kapak (TASARIM §6.2 `kor_paket.py`, D-18; [KU2] §4.5.4).

kor_paket.py izleme kiplerini bu modüle devreder (aynı CLI; Maske, yasak alan listesi ve sızıntı denetimi kor_paket'tendir):
  python kor_paket.py --kip animatik|kurgu|kesit [--tur N] --film <film>
  python kor_paket.py --kip kesici [--kaynak-kip animatik|kurgu] [--tur N] --film <film>
  python kor_paket.py --kip kapak [--tur N] --film <film>   (kapak.kor_paketi'ne gider; bu modül --kip kapak'ı oraya devreder)
  (doğrudan: python kor_paket_izleme.py … aynı seçenekler)
Kodda: isitsel_dokum(film, plan, kip) → [(plan_no, [satır…])] · paket_kur(film, kip, tur)
Çıktı (izleme kipleri):
  _KOR_PAKET/<kip>_t<tur>/<A|B|C>/<P0..P3>/{IZLE.md, sayfa_NN.jpg}   P0 = 0–120 sn; P1–P3 hikâye partileri; bölüm içinde parçalar
                                                                    RE izleme_parcasi_sn [240, 300] sahne sınırından kesilir
  _KOR_PAKET/<kip>_ilk2dk_t<tur>/{ILK2DK_<A|B|C>.md, P0/…, kapak.jpg}  başlık + gerçek kapak + ilk 120 sn
  _KOR_PAKET/<kip>_t<tur>/ESLESTIRICI/ANAHTAR.json · PAKET.json (_uretim, bölüm/parça dağılımı, sızıntı denetimi)
  ANIMATIK/ISITSEL_DOKUM.md (animatik kipinde; yoksa ya da eskiyse yazılır)
  kesici: _KOR_PAKET/kesici_t<tur>/{IZLE.md, KESME_GIRDI.md, SAYFALAR/sayfa_NN.jpg}
  kapak:  kapak.kor_paketi (_KOR_PAKET/kapak_t<tur>/; A11 kare-tarifcisi·kapak 1/ ve habersiz-seyirci·kapak SEYIRCI/)
Sayfa: RE izleme_sayfa_plan (6) plan; karede zaman kodu + plan numarası; RE izleme_kare_plan (animatik 1 kare + varsa bitiş görseli,
  kurgu 3 kare: baş + 0,15 sn, orta, son − 0,15 sn); sayfanın başında önceki sayfanın son karesi küçük. Animatikte karenin altında
  eylem şeridi (T1'deki adsız şerit). IZLE.md satırı: zaman, #plan, süre, duyulan [ekranda/ekran dışı + etiket], efekt, müzik.
Persona: izleme kiplerinde A, B klasörleri A personası, C klasörü B personası (RE seyirci_persona_izleme {A: 2, B: 1}; D-18).
Pakete GİRMEYENLER: amaç, duygu, risk, vuruş, merak/kurulum kimlikleri, ekranda_bilgi, seyirci_ogrenir, plan tipi, kadraj etiketi,
  kesme tipi, kopukluk adayları (K1ON/K1), önceki tur raporları. Paket kendi sızıntı denetiminden geçer; sızıntı varsa _RED/ ve 1.
Çıkış kodları: 0 BİTTİ · 1 HATA (girdi yok, sızıntı) · 4 ORTAM (kipin girdisi bu aşamada yok: kesit planı, video).
"""
import os, sys, re, json, glob, shutil, subprocess, argparse, statistics
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak
import kor_paket as kp
import zaman_cizelgesi_t1 as t1

SURUM = "kor_paket_izleme 1.0"
IZLEME = ("animatik", "kurgu", "kesit")
KARE_W, KARE_H = 400, 225
SAYFA_W = 1240
P0_SN = 120
YASAK_IZLEME = tuple(sorted(set(kp.KADRAJ.values()))) + ("plan tipi", "kesme tipi", "eylem kesmesi", "L kesme", "J kesme")


class OrtamHatasi(Exception):
    pass


def zk(sn, ondalik=True):
    sn = max(0.0, float(sn)); m = int(sn // 60); s = sn - m * 60
    return "%02d:%04.1f" % (m, s) if ondalik else "%02d:%02d" % (m, int(s))


def sn_tr(x): return ("%.1f" % float(x)).replace(".", ",")


# --- girdiler ---------------------------------------------------------------------------------------------------
def kaynak_coz(film, kip, tur):
    """(plan, plan_yolu, video_yolu|None)."""
    if kip == "animatik":
        plan, yol, n = t1.plan_oku(film, "T1", tur)
        if plan is None: plan, yol, n = t1.plan_oku(film, "T1")
        if plan is None: raise OrtamHatasi("KURGU_PLANI_T1 yok (zaman_cizelgesi --asama animatik önce koşar).")
        v = os.path.join(film, "ANIMATIK", "animatik_v%d.mp4" % n)
        return plan, yol, v if os.path.isfile(v) else None
    if kip == "kurgu":
        plan, yol, n = t1.plan_oku(film, "T2")
        if plan is None: raise OrtamHatasi("KURGU_PLANI_T2 yok (plan_kurgu, A16).")
        v = os.path.join(film, "KURGU", "onizleme_v%d.mp4" % tur)
        if not os.path.isfile(v):
            vs = sorted(glob.glob(os.path.join(film, "KURGU", "onizleme_v*.mp4")))
            v = vs[-1] if vs else None
        return plan, yol, v
    if kip == "kesit":
        ps = sorted(glob.glob(os.path.join(film, "KESIT", "KURGU_PLANI_KESIT_v*.json")),
                    key=lambda x: int(re.search(r"_v(\d+)\.json$", x).group(1)))
        if not ps: raise OrtamHatasi("KESIT/KURGU_PLANI_KESIT_v<N>.json yok (kurgu_render --kesit, A14a).")
        yol = ps[-1]; n = int(re.search(r"_v(\d+)\.json$", yol).group(1))
        v = os.path.join(film, "KESIT", "kesit_v%d.mp4" % n)
        return ortak.json_oku(yol), yol, v if os.path.isfile(v) else None
    raise OrtamHatasi("bilinmeyen izleme kipi: %s" % kip)


def ses_cizelgesi(film, kip):
    for ad in (("SES_CIZELGESI_T1.json",) if kip == "animatik" else ()) + ("SES_CIZELGESI.json",):
        s = ortak.json_oku(os.path.join(film, "KURGU", ad))
        if isinstance(s, dict): return s
    return {}


def _ses_adi(x):
    t = x.get("tarif") or x.get("tarif_tr") or x.get("kategori")
    if t: return str(t).replace("_", " ")
    b = os.path.splitext(os.path.basename(str(x.get("dosya") or x.get("id") or "")))[0]
    b = re.sub(r"[\d_]+", " ", b).strip()
    return re.sub(r"\b(DIS|IC|E\w?)\b", "", b).strip() or "ses"


def asr_wer(film):
    d = ortak.json_oku(os.path.join(film, "SESLER", "diyalog.json"), {}) or {}
    out = {}
    for rid, v in (d.get("replikler") or {}).items() if isinstance(d.get("replikler"), dict) else []:
        w = ((v or {}).get("metin_kapisi") or {}).get("wer")
        if w is None: w = ((v or {}).get("donusum") or {}).get("asr_wer_sonra")
        if isinstance(w, (int, float)): out[rid] = float(w)
    return out


# --- işitsel döküm ([SM2] SB5 madde 5; ad maskeleme kor_paket.Maske) -------------------------------------------------
def isitsel_dokum(film, plan, kip, mk=None, sahneler=None):
    """[(plan_no, [satır…], maske_durumu)] — sırayla; mk verilirse durumunu ilerletir."""
    film = os.path.abspath(film)
    h = ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}
    sahneler = sahneler if sahneler is not None else (ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {})
    kar = dict(h.get("karakterler") or {})
    for kid, v in (sahneler.get("karakterler") or {}).items(): kar.setdefault(kid, {}).setdefault("tarif", (v or {}).get("tarif"))
    mk = mk or kp.Maske(kar, kp.ses_etiketleri(film))
    sp = {p.get("no"): p for p in sahneler.get("sahneler") or [] if isinstance(p, dict)}
    rep_h = {r.get("id"): r for r in h.get("replikler") or [] if isinstance(r, dict)}
    sc = ses_cizelgesi(film, kip); wer = asr_wer(film); wer_esik = t1.E("anlasilmayan_konusma_wer")
    diy = {}
    for d in plan.get("diyalog") or []: diy.setdefault(d.get("plan"), []).append(d)
    efekt = {}
    for e in sc.get("efektler") or []: efekt.setdefault(e.get("plan"), []).append(_ses_adi(e))
    amb = {}
    for a in sc.get("ambiyans") or []: amb.setdefault(a.get("sahne_grubu"), _ses_adi(a))
    muz = sorted([m for m in sc.get("muzik") or [] if isinstance(m.get("cizelge_bas"), (int, float))], key=lambda m: m["cizelge_bas"])
    ses_yok = [s for s in sc.get("sessizlik") or []]
    out, son_sahne = [], None
    kartlar = {}
    for k in plan.get("kartlar") or []: kartlar.setdefault(k.get("plan"), []).append(k)
    for p in plan.get("planlar") or []:
        no = p.get("plan"); bas = float(p.get("cizelge_bas") or 0); sure = float(p.get("sure") or 0)
        s = sp.get(no) or {}; z = s.get("zanaat") or {}; sat = []
        for k in kartlar.get(no, []):
            sat.append("ekranda yazı: %s" % k.get("metin")); mk.duyuldu(k.get("metin"))
        if p.get("goruntu", {}).get("tur") == "kart" and p.get("goruntu", {}).get("metin"):
            sat.append("ekranda yazı: %s" % p["goruntu"]["metin"]); mk.duyuldu(p["goruntu"]["metin"])
        gorunen = {x.get("id") for x in z.get("kadrajdakiler") or [] if isinstance(x, dict)}
        for d in sorted(diy.get(no, []), key=lambda d: float(d.get("plan_ofset") or 0)):
            gor = bool(d.get("gorunen_konusan")) and not d.get("ekran_disi") and d.get("karakter") in gorunen
            etk = mk.anan(d.get("karakter"), gor).strip("[]")
            yer = "ekranda" if gor else "ekran dışı"
            metin = d.get("metin") or (rep_h.get(d.get("replik")) or {}).get("metin") or ""
            if kip != "animatik" and wer.get(d.get("replik"), 0) > wer_esik:
                sat.append("duyulan [%s, %s]: (anlaşılmayan konuşma)" % (yer, etk))
            else:
                sat.append("duyulan [%s, %s]: \"%s\"" % (yer, etk, metin))
                mk.duyuldu(metin, (rep_h.get(d.get("replik")) or {}).get("ad_soyler") or ())
        ek = []
        sg = p.get("sahne_grubu")
        if sg != son_sahne and amb.get(sg): ek.append("ortam: " + mk.maskele(amb[sg]))
        son_sahne = sg
        if efekt.get(no): ek.append("efekt: " + mk.maskele(", ".join(efekt[no])))
        elif not sc:
            fs = re.sub(r"^\s*Sound:\s*", "", str((z.get("ses") or {}).get("flow_sound") or "")).strip()
            fs = re.sub(r"\s*No music\.?\s*$", "", fs, flags=re.I).strip().rstrip(".")
            if fs: ek.append("efekt: " + mk.maskele(fs))
        mz = [m for m in muz if bas <= m["cizelge_bas"] < bas + sure]
        mb = [m for m in muz if bas <= m["cizelge_bas"] + float(m.get("sure") or 0) < bas + sure]
        if mz: ek.append("müzik: " + ", ".join("giriyor (%s)" % str(m.get("tur") or m.get("duygu") or "alt müzik").replace("_", " ") for m in mz))
        elif mb: ek.append("müzik: susuyor")
        elif not muz: ek.append("müzik: yok")
        if any(bas <= float(x.get("cizelge_bas") or -1) < bas + sure for x in ses_yok): ek.append("sessizlik")
        if ek: sat.append(" · ".join(ek))
        out.append((no, sat, mk.kopya_durum()))
    return out, mk


def isitsel_dokum_yaz(film, plan, kip="animatik"):
    satirlar, _ = isitsel_dokum(film, plan, kip)
    bas = {p["plan"]: p for p in plan.get("planlar") or []}
    m = ["# İşitsel döküm (%s · %s)" % (kip, plan.get("cizelge") or ""), "",
         "Adlar ekranda söylenene kadar maskelidir; her satır o planda duyulanı yazar.", ""]
    for no, sat, _ in satirlar:
        p = bas[no]; m.append("- [%s] #%s · %s sn" % (zk(p["cizelge_bas"]), _no(no), sn_tr(p["sure"])))
        m += ["  " + x for x in sat] or ["  (sessiz)"]
    hedef = os.path.join(film, "ANIMATIK" if kip == "animatik" else "KURGU", "ISITSEL_DOKUM.md")
    kp._yaz(hedef, "\n".join(m) + "\n")
    return hedef


def _no(no):
    try: return ("%g" % float(no))
    except (TypeError, ValueError): return str(no)


# --- bölümler ve parçalar -----------------------------------------------------------------------------------------
def bolumle(plan):
    """[(bolum, parca, [plan…])] — P0 = 0–120 sn; sonra parti (P1–P3); bölüm içinde 240–300 sn'lik parçalar (sahne sınırı)."""
    lo, hi = t1.E("izleme_parcasi_sn") or [240, 300]
    ps = plan.get("planlar") or []
    p0 = [p for p in ps if float(p.get("cizelge_bas") or 0) < P0_SN]
    kalan = [p for p in ps if float(p.get("cizelge_bas") or 0) >= P0_SN]
    out = [("P0", 0, p0)] if p0 else []
    gruplar = {}
    for p in kalan: gruplar.setdefault(kp.bolum_adi(p.get("parti")), []).append(p)
    no = 1
    for bol in ("P1", "P2", "P3"):
        planlar = gruplar.get(bol) or []
        sahneler, cur = [], []
        for p in planlar:
            if cur and p.get("sahne_grubu") != cur[-1].get("sahne_grubu"): sahneler.append(cur); cur = []
            cur.append(p)
        if cur: sahneler.append(cur)
        parca, top = [], 0.0
        for s in sahneler:
            ssure = sum(float(p["sure"]) for p in s)
            if parca and (top >= lo or top + ssure > hi): out.append((bol, no, parca)); no += 1; parca, top = [], 0.0
            if ssure > hi:                                       # tek sahne parçadan uzun: plan sınırından böl
                for p in s:
                    if parca and top + float(p["sure"]) > hi: out.append((bol, no, parca)); no += 1; parca, top = [], 0.0
                    parca.append(p); top += float(p["sure"])
                continue
            parca += s; top += ssure
        if parca: out.append((bol, no, parca)); no += 1
    return out


# --- kareler ve sayfalar -------------------------------------------------------------------------------------------
def _font(boy, italik=False):
    from PIL import ImageFont
    adlar = (["ariali.ttf", "DejaVuSans-Oblique.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"] if italik else []) + \
            ["arial.ttf", "segoeui.ttf", "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for a in adlar:
        try: return ImageFont.truetype(a, boy)
        except OSError: continue
    try: return ImageFont.load_default(size=boy)
    except TypeError: return ImageFont.load_default()


def yer_tutucu_gorsel(no, w, h, metin=None):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (w, h), (96, 96, 96)); d = ImageDraw.Draw(im)
    d.text((w // 20, h // 3), "#%s · görsel hazır değil" % _no(no), fill=(230, 230, 230), font=_font(max(10, h // 12)))
    if metin: d.text((w // 20, h // 2), metin[:80], fill=(220, 220, 220), font=_font(max(9, h // 16)))
    return im


def kare_al(film, video, t, plan, hangi, w=KARE_W, h=KARE_H):
    """PIL görüntüsü: videodan t anındaki kare; video yoksa kaynak görsel / bitiş görseli / yer tutucu."""
    from PIL import Image
    if video:
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % max(0.0, t), "-i", video, "-frames:v", "1",
                            "-vf", "scale=%d:%d" % (w, h), "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
        if r.returncode == 0 and r.stdout:
            import io
            return Image.open(io.BytesIO(r.stdout)).convert("RGB")
    g = plan.get("goruntu") or {}
    yol = g.get("bitis_dosya") if hangi == "bitis" else g.get("dosya")
    if yol and os.path.isfile(os.path.join(film, yol)):
        return Image.open(os.path.join(film, yol)).convert("RGB").resize((w, h))
    return yer_tutucu_gorsel(plan.get("plan"), w, h)


def plan_kareleri(film, video, p, kip):
    bas = float(p["cizelge_bas"]); s = float(p["sure"])
    if kip == "animatik":
        ks = [(bas + min(0.15, s / 4), "bas")]
        if (p.get("goruntu") or {}).get("bitis_dosya"): ks.append((bas + max(0.0, s - 0.05), "bitis"))
    else:
        ks = [(bas + min(0.15, s / 4), "bas"), (bas + s / 2, "orta"), (bas + max(0.0, s - 0.15), "son")]
    return [kare_al(film, video, t, p, hangi) for t, hangi in ks]


def sayfa_ciz(satirlar, onceki, yol):
    """satirlar: [(plan, [kareler], baslik, alt_yazi)]; onceki: önceki sayfanın son karesi (PIL) ya da None."""
    from PIL import Image, ImageDraw
    alt_h = 44; ust = 130 if onceki is not None else 10
    H = ust + len(satirlar) * (KARE_H + alt_h + 10) + 10
    im = Image.new("RGB", (SAYFA_W, H), (18, 18, 18)); d = ImageDraw.Draw(im)
    f = _font(16); fi = _font(15, italik=True)
    if onceki is not None:
        im.paste(onceki.resize((200, 112)), (10, 8)); d.text((220, 50), "(önceki sayfanın son karesi)", fill=(160, 160, 160), font=f)
    y = ust
    for p, kareler, baslik, alt in satirlar:
        x = 10
        for k in kareler[:3]:
            im.paste(k, (x, y)); x += KARE_W + 10
        d.rectangle([10, y, 10 + 150, y + 22], fill=(0, 0, 0)); d.text((14, y + 2), baslik, fill=(255, 230, 120), font=f)
        if alt: d.text((10, y + KARE_H + 6), alt[:150], fill=(220, 220, 220), font=fi)
        y += KARE_H + alt_h + 10
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    im.save(yol, quality=82)
    return kareler[-1] if satirlar and satirlar[-1][1] else onceki


# --- paket ---------------------------------------------------------------------------------------------------------
def _persona_satiri(klasor):
    es = kp.PERSONA_ESLEME["izleme"]
    return kp.PERSONA[es[klasor]], es[klasor]


def izleme_metni(kip, bol, parcalar, dokum, persona_satiri):
    bas = ["# Bölüm %s · %s" % (bol, "animatik" if kip == "animatik" else "kurgu"), "", persona_satiri, "",
           "Sayfaları (sayfa_NN.jpg) sırayla aç; her karenin altındaki satırlar o planda duyulanlardır." +
           (" Kareler planların durağan başlangıç kareleridir; altındaki italik yazı o planda görünen hareketi anlatır." if kip == "animatik" else ""),
           "Her parçayı bitirince o parçanın kısa notunu al; bölümün sonunda raporunu yaz.", ""]
    for parca, sayfalar in parcalar:
        bas += ["## Parça %d" % parca, ""]
        for sad, ps in sayfalar:
            nm = re.search(r"(\d+)\.jpg$", sad)
            bas += ["### Sayfa %s (%s)" % (nm.group(1) if nm else "?", sad)]
            for p in ps:
                bas.append("- [%s] #%s · %s sn" % (zk(p["cizelge_bas"]), _no(p["plan"]), sn_tr(p["sure"])))
                bas += ["  " + x for x in dokum.get(p["plan"], [])] or ["  (sessiz)"]
            bas.append("")
    return "\n".join(bas) + "\n"


def tur_bul(arg): return kp.tur_bul(arg)


def paket_kur(film, kip, tur, gorev=None):
    film = os.path.abspath(film)
    plan, pyol, video = kaynak_coz(film, kip, tur)
    sahneler = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
    h = ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}
    kar = dict(h.get("karakterler") or {})
    for kid, v in (sahneler.get("karakterler") or {}).items(): kar.setdefault(kid, {}).setdefault("tarif", (v or {}).get("tarif"))
    dok, mk = isitsel_dokum(film, plan, kip, sahneler=sahneler)
    dokum = {no: sat for no, sat, _ in dok}; durum = {no: d for no, _, d in dok}
    if kip == "animatik": isitsel_dokum_yaz(film, plan, kip)
    bolumler = bolumle(plan)
    if not bolumler: raise kp.GirdiHatasi("Pakete girecek plan yok.")
    kok_ad = "%s_t%d" % (kip, tur)
    hedef = os.path.join(film, "_KOR_PAKET", kok_ad); hedef_ik = os.path.join(film, "_KOR_PAKET", "%s_ilk2dk_t%d" % (kip, tur))
    gecici = os.path.join(film, "_KOR_PAKET", "." + kok_ad + ".yeni"); gecici_ik = gecici + "_ik"
    for g in (gecici, gecici_ik):
        if os.path.exists(g): kp.eskiyi_tasi(film, g)
    sayfa_n = int(t1.E("izleme_sayfa_plan") or 6)
    ortak_d = os.path.join(gecici, "_SAYFALAR")
    sayfa_no, onceki = 0, None
    bol_parcalar = {}; bol_son = {}
    for bol, parca, ps in bolumler:
        sayfalar = []
        for i in range(0, len(ps), sayfa_n):
            sayfa_no += 1; ad = "sayfa_%02d.jpg" % sayfa_no
            sat = []
            for p in ps[i:i + sayfa_n]:
                kareler = plan_kareleri(film, video, p, kip)
                serit = " | ".join(x["metin"] for x in p.get("serit") or []) if kip == "animatik" else ""
                sat.append((p, kareler, "%s #%s" % (zk(p["cizelge_bas"], False), _no(p["plan"])), mk_maskele_bas(serit, kar, durum, p)))
            onceki = sayfa_ciz(sat, onceki, os.path.join(ortak_d, ad))
            sayfalar.append((ad, ps[i:i + sayfa_n]))
        bol_parcalar.setdefault(bol, []).append((parca, sayfalar))
        bol_son[bol] = durum.get(ps[-1]["plan"], set())
    mk_adlari = {}
    for klasor in kp.KLASORLER:
        satir, _ = _persona_satiri(klasor)
        for bol in kp.BOLUMLER:
            d = os.path.join(gecici, klasor, bol); os.makedirs(d, exist_ok=True)
            parcalar = bol_parcalar.get(bol) or []
            if not parcalar:
                kp._yaz(os.path.join(d, "IZLE.md"), "# Bölüm %s\n\n%s\n\n(Bu bölümde plan yok; raporuna yalnız 'bölüm boş' yaz.)\n" % (bol, satir))
            else:
                kp._yaz(os.path.join(d, "IZLE.md"), izleme_metni(kip, bol, parcalar, dokum, satir))
                for _, sayfalar in parcalar:
                    for ad, _ in sayfalar: shutil.copy2(os.path.join(ortak_d, ad), os.path.join(d, ad))
            mk_adlari["%s/%s/IZLE.md" % (klasor, bol)] = mk.kurulmamis_adlar(bol_son.get(bol, set()))
    # ilk 2 dk: başlık + gerçek kapak + P0
    b = h.get("baslik") or {}; baslik = b.get("secilen") if isinstance(b, dict) else b
    kapak = kapak_bul(film)
    p0 = bol_parcalar.get("P0") or []
    for klasor in kp.KLASORLER:
        satir, _ = _persona_satiri(klasor)
        m = ["# İlk 2 dakika", "", satir, ""]
        if baslik: m.append("BAŞLIK: " + str(baslik))
        if kapak: m.append("KAPAK: kapak.jpg")
        else:
            kt = next((v.get("ekranda") for v in h.get("vaat_sozlesmesi") or [] if isinstance(v, dict) and v.get("oge") == "kapak_imgesi"), None)
            if kt: m.append("KAPAK: " + kp.Maske(kar).maskele(kt))
        m += ["", "Soru: 30 sn'den sonra kalır mıydın? 2. dakikanın sonunda devam eder miydin? Neden? Başlıkta ve kapakta vaat edileni gördün mü?", ""]
        if p0: m.append(izleme_metni(kip, "P0", p0, dokum, "").split("\n", 4)[-1])
        kp._yaz(os.path.join(gecici_ik, "ILK2DK_%s.md" % klasor), "\n".join(m) + "\n")
    if p0:
        os.makedirs(os.path.join(gecici_ik, "P0"), exist_ok=True)
        for _, sayfalar in p0:
            for ad, _ in sayfalar: shutil.copy2(os.path.join(gecici, "A", "P0", ad), os.path.join(gecici_ik, "P0", ad))
    if kapak: shutil.copy2(kapak, os.path.join(gecici_ik, "kapak.jpg"))
    ortak.atomik_yaz(os.path.join(gecici, "ESLESTIRICI", "ANAHTAR.json"), kp.anahtar(h, mk))
    yasak = kp.yasak_degerler(h, sahneler)
    hatalar = kp.denetle_klasor(gecici, yasak, mk_adlari)
    son_p0 = p0[-1][1][-1][1][-1]["plan"] if p0 else None
    ik_adlar = mk.kurulmamis_adlar(durum.get(son_p0, set()))
    hatalar += kp.denetle_klasor(gecici_ik, yasak, {"ILK2DK_%s.md" % k: ik_adlar for k in kp.KLASORLER})
    hatalar += izleme_yasak_denetle(gecici) + izleme_yasak_denetle(gecici_ik)
    return _yayimla(film, kip, tur, gorev, gecici, gecici_ik, hedef, hedef_ik, hatalar, pyol, video, bolumler, plan)


def mk_maskele_bas(serit, kar, durum, p):
    """Şerit T1'de zaten adsızdır; yine de plan başındaki maske durumuna göre ad kalmadığını garanti eder."""
    if not serit: return ""
    m = kp.Maske(kar); m.kurulan = set()
    return m.maskele(serit)


def izleme_yasak_denetle(kok):
    """Kadraj etiketi, plan tipi ve kesme tipi adları izleme paketine girmez (D-18, [KU2] İ-7)."""
    out = []
    for dp, _, fs in os.walk(kok):
        if "ESLESTIRICI" in dp.replace("\\", "/").split("/"): continue
        for f in fs:
            if not f.endswith(".md"): continue
            with open(os.path.join(dp, f), encoding="utf-8") as fh: metin = fh.read()
            acik = re.sub(r"\"[^\"]*\"", "", metin)
            for y in YASAK_IZLEME:
                if re.search(r"(?<![\w])" + re.escape(y) + r"(?![\w])", acik, re.I):
                    out.append({"dosya": os.path.relpath(os.path.join(dp, f), kok), "tur": "izleme_yasak", "deger": y})
    return out


def kapak_bul(film):
    for d in ("YAYIN/kapak_1.jpg", "YAYIN/KAPAK.jpg", "YAYIN/kapak_secilen.jpg"):
        if os.path.isfile(os.path.join(film, d)): return os.path.join(film, d)
    ks = sorted(glob.glob(os.path.join(film, "YAYIN", "kapak_*.jpg")))
    return ks[0] if ks else None


def _yayimla(film, kip, tur, gorev, gecici, gecici_ik, hedef, hedef_ik, hatalar, pyol, video, bolumler, plan):
    manifest = {"_surum": 1, "_uretim": {"asama": os.environ.get("YZ_FILM_ASAMA") or {"animatik": "A12", "kurgu": "A16", "kesit": "A14a"}.get(kip),
                                         "gorev": gorev, "girdi_imza": t1.sha(pyol), "arac_surum": SURUM, "esik_surum": None,
                                         "sonuc": "HATA" if hatalar else "GEC", "zaman": t1.simdi(), "ortam": t1.ortam()},
                "kip": kip, "tur": tur, "kaynak": {"kurgu_plani": os.path.relpath(pyol, film).replace("\\", "/"),
                                                   "video": os.path.relpath(video, film).replace("\\", "/") if video else None},
                "klasorler": dict(kp.PERSONA_ESLEME["izleme"]),
                "bolumler": {b: [] for b in kp.BOLUMLER}, "parcalar": [],
                "ilk2dk": "_KOR_PAKET/%s_ilk2dk_t%d" % (kip, tur),
                "sizinti": {t: sum(1 for x in hatalar if x["tur"] == t) for t in ("yasak_alan", "ad", "izleme_yasak")}, "hatalar": hatalar[:50]}
    for bol, parca, ps in bolumler:
        manifest["bolumler"][bol] += [p["plan"] for p in ps]
        manifest["parcalar"].append({"bolum": bol, "parca": parca, "bas_sn": ps[0]["cizelge_bas"],
                                     "sure_sn": round(sum(float(p["sure"]) for p in ps), 3), "plan": len(ps)})
    if not video: manifest["not"] = "video yok: kareler kaynak görsellerden (yer tutucu dahil)"
    if hatalar:
        red = os.path.join(film, "_KOR_PAKET", "_RED"); os.makedirs(red, exist_ok=True)
        import time
        for g in (gecici, gecici_ik):
            if os.path.exists(g): shutil.move(g, os.path.join(red, os.path.basename(g).lstrip(".") + "_" + time.strftime("%Y%m%d_%H%M%S")))
        ortak.atomik_yaz(os.path.join(red, "%s_t%d_SIZINTI.json" % (kip, tur)), manifest)
        return 1, manifest
    ortak.atomik_yaz(os.path.join(gecici, "PAKET.json"), manifest)
    for g, h_ in ((gecici, hedef), (gecici_ik, hedef_ik)):
        kp.eskiyi_tasi(film, h_); os.replace(g, h_)
    return 0, manifest


# --- kesici ------------------------------------------------------------------------------------------------------
def seyirci_ozeti(film, kip):
    """(ortak sıkılma anları, medyan ilgi eğrisi, tur) — en son seyirci kararından; yoksa boş."""
    kararlar = sorted(glob.glob(os.path.join(film, "_RAPOR", "SEYIRCI_KARAR_%s_t*.json" % kip.upper())),
                      key=lambda x: int(re.search(r"_t(\d+)\.json$", x).group(1)))
    if not kararlar: return [], [], None
    k = ortak.json_oku(kararlar[-1], {}) or {}
    tur = k.get("tur")
    ortak_s = [{"an": a, "seyirci": len(v)} for a, v in (k.get("sikilma") or {}).items() if len(v) >= (t1.E("sikilma_ortak_isaret_min") or 2)]
    dk = {}
    for p in glob.glob(os.path.join(film, "_RAPOR", "SEYIRCI", "%s_t%s" % (kip, tur), "s*_rapor.json")):
        r = ortak.json_oku(p, {}) or {}
        for i in r.get("ilgi") or []:
            z = (i.get("konum") or {}).get("zaman_bas")
            try: m = int(str(z).split(":")[0]) if z is not None else None
            except ValueError: m = None
            if m is not None and isinstance(i.get("puan"), (int, float)): dk.setdefault(m, []).append(i["puan"])
    egri = [{"dakika": m, "medyan_ilgi": statistics.median(v)} for m, v in sorted(dk.items())]
    return ortak_s, egri, tur


def kesici_kur(film, kaynak_kip, tur, gorev=None):
    film = os.path.abspath(film)
    plan, pyol, video = kaynak_coz(film, kaynak_kip, tur)
    sahneler = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
    h = ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}
    dok, mk = isitsel_dokum(film, plan, kaynak_kip, sahneler=sahneler)
    dokum = {no: s for no, s, _ in dok}
    kok_ad = "kesici_t%d" % tur
    hedef = os.path.join(film, "_KOR_PAKET", kok_ad); gecici = os.path.join(film, "_KOR_PAKET", "." + kok_ad + ".yeni")
    if os.path.exists(gecici): kp.eskiyi_tasi(film, gecici)
    kar = dict(h.get("karakterler") or {})
    n = int(t1.E("izleme_sayfa_plan") or 6); ps = plan.get("planlar") or []; sayfalar = []; onceki = None
    for i in range(0, len(ps), n):
        ad = "sayfa_%02d.jpg" % (i // n + 1); sat = []
        for p in ps[i:i + n]:
            serit = " | ".join(x["metin"] for x in p.get("serit") or []) if kaynak_kip == "animatik" else ""
            sat.append((p, plan_kareleri(film, video, p, kaynak_kip), "%s #%s" % (zk(p["cizelge_bas"], False), _no(p["plan"])),
                        mk_maskele_bas(serit, kar, {}, p)))
        onceki = sayfa_ciz(sat, onceki, os.path.join(gecici, "SAYFALAR", ad)); sayfalar.append((ad, ps[i:i + n]))
    kp._yaz(os.path.join(gecici, "IZLE.md"), izleme_metni(kaynak_kip, "FILM", [(1, [("SAYFALAR/" + a, x) for a, x in sayfalar])], dokum,
                                                         "Filmi seyirci gibi baştan sona izle; sonra KESME_GIRDI.md'deki soruyu cevapla."))
    sik, egri, st = seyirci_ozeti(film, kaynak_kip)
    oner = t1.E("kesme_turu_oneri") or {"plan": 10, "sahne": 2}
    m = ["# Kesme girdisi", "", "Tek soru: hangi en çok %d planı ya da %d sahneyi atarsak film daha iyi olur?" % (oner["plan"], oner["sahne"]),
         "Her öneri için gerekçe, beklenen kazanç (sn) ve 'seyirci olarak neyi kaybedebilirim' notu yaz (CIKTI/KESME_ONERI.json).", "",
         "## Plan sırası ve süreleri", "", "| sıra | plan | sahne | başlangıç | süre (sn) |", "|---|---|---|---|---|"]
    for k, p in enumerate(ps, 1):
        m.append("| %d | #%s | %s | %s | %s |" % (k, _no(p["plan"]), p.get("sahne_grubu") or "—", zk(p["cizelge_bas"], False), sn_tr(p["sure"])))
    m += ["", "## Seyircilerin ortak sıkılma anları", ""]
    m += ["- %s (%d seyirci)" % (x["an"], x["seyirci"]) for x in sik] or ["- henüz seyirci turu yok" if st is None else "- yok"]
    m += ["", "## Medyan ilgi eğrisi (dakika başına, 1–10)", ""]
    m += ["- %d. dk: %s" % (x["dakika"], ("%g" % x["medyan_ilgi"])) for x in egri] or ["- ölçüm yok"]
    kp._yaz(os.path.join(gecici, "KESME_GIRDI.md"), "\n".join(m) + "\n")
    yasak = kp.yasak_degerler(h, sahneler)
    hatalar = kp.denetle_klasor(gecici, yasak, {"IZLE.md": mk.kurulmamis_adlar(mk.kopya_durum()), "KESME_GIRDI.md": mk.kurulmamis_adlar(mk.kopya_durum())}) + izleme_yasak_denetle(gecici)
    manifest = {"_surum": 1, "_uretim": {"asama": "A12" if kaynak_kip == "animatik" else "A16", "gorev": gorev, "girdi_imza": t1.sha(pyol),
                                         "arac_surum": SURUM, "esik_surum": None, "sonuc": "HATA" if hatalar else "GEC", "zaman": t1.simdi(),
                                         "ortam": t1.ortam()},
                "kip": "kesici", "kaynak_kip": kaynak_kip, "tur": tur, "plan_sayisi": len(ps), "sayfa": len(sayfalar),
                "seyirci_turu": st, "sizinti": len(hatalar), "hatalar": hatalar[:50]}
    if hatalar:
        red = os.path.join(film, "_KOR_PAKET", "_RED"); os.makedirs(red, exist_ok=True)
        shutil.move(gecici, os.path.join(red, kok_ad + "_red")); ortak.atomik_yaz(os.path.join(red, kok_ad + "_SIZINTI.json"), manifest)
        return 1, manifest
    ortak.atomik_yaz(os.path.join(gecici, "PAKET.json"), manifest)
    kp.eskiyi_tasi(film, hedef); os.replace(gecici, hedef)
    return 0, manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description="Kör paket (izleme kipleri).")
    ap.add_argument("--kip"); ap.add_argument("--tur", type=int); ap.add_argument("--film"); ap.add_argument("--kaynak-kip")
    ap.add_argument("--kaynak"); ap.add_argument("--saglayici"); ap.add_argument("--json", action="store_true"); ap.add_argument("--denetle")
    o = ap.parse_args(argv)
    film = o.film or os.environ.get("YZ_FILM_FILM")
    if not film or not os.path.isdir(film): print("!! --film <film klasörü> gerekli."); return 1
    gorev = os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None
    tur = tur_bul(o.tur)
    try:
        if o.kip in IZLEME: kod, m = paket_kur(film, o.kip, tur, gorev)
        elif o.kip == "kesici":
            kaynak = o.kaynak_kip or ("kurgu" if (os.environ.get("YZ_FILM_ASAMA") or "").startswith("A16") else "animatik")
            kod, m = kesici_kur(film, kaynak, tur, gorev)
        elif o.kip == "kapak": return kp.kapak_paketi(list(sys.argv[1:] if argv is None else argv))     # tek yol: kapak.kor_paketi (kor_paket ile aynı)
        else: print("!! Bilinmeyen izleme kipi: %s" % o.kip); return 1
    except OrtamHatasi as e: print("!! " + str(e)); return 4
    except kp.GirdiHatasi as e: print("!! " + str(e)); return 1
    if kod: print("!! Kör pakette sızıntı bulundu; paket yayımlanmadı (_KOR_PAKET/_RED/)."); return kod
    print(json.dumps({"kip": o.kip, "tur": tur, "parca": len(m.get("parcalar") or []), "sizinti": m.get("sizinti")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
