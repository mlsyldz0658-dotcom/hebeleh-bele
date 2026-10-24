"""KURGU UYGULA — kurgucunun işlem listesini doğrular ve uygular (TASARIM §6.7; [KU2] §4.5.6, KR4; AR3 B4: plan → doğrula → uygula).

Kullanım:
  python kurgu_uygula.py --kuru <KURGU_KARARLARI.json> --film <film>        yalnız doğrular (SubagentStop kancası; 0 temiz · 1 HATA)
  python kurgu_uygula.py [--uygula] [--kararlar <yol>] [--cizelge T1|T2] [--tur N] --film <film>
      doğrular; HATA yoksa en son KURGU_PLANI_<T> sürümüne uygular → KURGU/surumler/KURGU_PLANI_<T>_v<N+1>.json,
      KURGU/KURGU_DUZEN_<T>.json (kalıcı işlem katmanı; zaman_cizelgesi her yeniden kuruluşta yeniden uygular),
      *_iste işlemleri → KURGU/ISTEKLER_<T>_t<n>.json (+ yönetmen/yazar istekleri KUYRUK/YENIDEN_YAZ), yeniden_cek → KUYRUK/YENIDEN_URET
      (kuyruk.py; 0 kredi kuralı orada da zorlanır), rapor _RAPOR/KURGU_UYGULA_<T>_t<n>.json.
  Varsayılan karar dosyası: KURGU/KURGU_KARARLARI_<T>_t<tur>.json (A16n'de NOT_CEVAPLARI.json'daki "islemler").
Kodda: kurgu_uygula.denetle(islemler, plan, sahneler, cizelge) → (hatalar, bayraklar) · uygula(plan, islemler, sahneler) ·
  duzen_uygula(plan, islemler, sahneler) (zaman_cizelgesi_t1 çağırır).
İşlemler ([KU2] §4.5.6): kirp, uzat, sira, jl, ekran_disi, kopru_replik_iste, ortu, alternatif, bol, ayna, kadraj, hiz, kart, efekt_iste,
  kes, kes_sahne_iste, yer_tutucu, yeniden_cek, yeni_plan_iste, diyalog_kaydir {replik, sn} (dudak_denetim S3.1 → KURGU/S3_ONERI_v<N>.json;
  |sn| ≤ diyalog_kaydir_max_sn, plan_ofset'e eklenir: `--kararlar KURGU/S3_ONERI_v<N>.json`).
SES İSTEKLERİ (T2/T3): KURGU/SES_ISTEKLERI.json'daki yapılmamış ekran_disi istekleri (ses_karar, ekran_disi_tts) işlem listesine eklenir;
  kurgucu aynı repliğe karar verdiyse onunki geçer, yoksa B9'dan geçen en yakın plan seçilir (bulunamazsa BAYRAK). Uygulanan istek
  yapildi: true işaretlenir. Karar dosyası yoksa yalnız bu istekler uygulanır.
Denetim (her işlem): bilinen op · kok_neden veri/kok_neden.json'da · bulgu dolu · plan/replik var · `kullanim_kaynak: kullanici` ya da
  kilitli plana dokunulmaz · sira: yalnız etkisiz planlar yer değiştirir (dondurulmuş durum zıplamasın, Y58) ve yeni sıra aynı sahne
  grubunun permütasyonudur · jl taşması RE l_kesme_aralik_sn / j_kesme_aralik_sn içinde, üstüne binilen plan ≥ taşma + RE
  l_kesme_alici_plan_ek_sn · ekran_disi: üstüne konan planda başka birinin ağzı görünmez (B9) · hiz RE hiz_aralik_diyalogsuz ve yalnız
  diyalogsuz plan · kadraj ≤ RE yeniden_kadraj_max · ayna _derlenir.ayna_yasak değilse · kes: kesme simülasyonunda (KESME_SIMULE_<T>.json)
  HATA'sız geçmiş öneri; simülasyondan temiz geçenlerin en az RE kesme_turu_oneri.uygulama_orani_min'i uygulanmalı · T1'de video işlemleri
  (alternatif, bol) yok · yeniden_cek: sifir_kredi {basamaklar, gerekce} zorunlu (D-31).
Çıkış kodları: 0 tamam · 1 HATA (hiçbir şey yazılmadı) · 2 girdi yok · 4 kullanım.
"""
import os, sys, re, json, glob, math, argparse, copy
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "kurgu_uygula 1.0"
OPLAR = ("kirp", "uzat", "sira", "jl", "ekran_disi", "kopru_replik_iste", "ortu", "alternatif", "bol", "ayna", "kadraj", "hiz", "kart",
         "efekt_iste", "kes", "kes_sahne_iste", "yer_tutucu", "yeniden_cek", "yeni_plan_iste", "diyalog_kaydir")
ISTE = ("kopru_replik_iste", "efekt_iste", "kes_sahne_iste", "yeni_plan_iste")
YALNIZ_VIDEO = ("alternatif", "bol")
KART_TURLERI = ("yer_zaman", "baslik", "bolum", "kopru", "jenerik", "seri_kancasi")
VARS = {"l_kesme_aralik_sn": [0.3, 2.5], "j_kesme_aralik_sn": [0.3, 0.8], "l_kesme_alici_plan_ek_sn": 0.5,
        "hiz_aralik_diyalogsuz": [0.9, 1.15], "yeniden_kadraj_max": 0.1, "kesme_turu_oneri": {"plan": 10, "sahne": 2, "uygulama_orani_min": 0.5},
        "kullanim_bas_min_sn": 0.3, "diyalog_kaydir_max_sn": 0.5}


class KurguHatasi(Exception):
    pass


def E(ad):
    import zaman_cizelgesi_t1 as t1
    v = t1.E(ad)
    return VARS.get(ad) if v is None else v


def kok_nedenler():
    d = ortak.json_oku(os.path.join(HERE, "veri", "kok_neden.json"), {}) or {}
    k = dict(d.get("kok_nedenler") or {})
    for ad, v in (d.get("es_anlamlar") or {}).items(): k.setdefault(ad, {"es": v})
    return k


def _planlar(plan): return {p.get("plan"): p for p in plan.get("planlar") or []}


def _sahne_plani(sahneler):
    return {p.get("no"): p for p in (sahneler or {}).get("sahneler") or [] if isinstance(p, dict)}


def _kilitli(p):
    g = p.get("goruntu") or {}
    return g.get("kullanim_kaynak") == "kullanici" or bool(g.get("kullanim_kilit"))


def _simule(film, cizelge):
    return ortak.json_oku(os.path.join(film, "_RAPOR", f"KESME_SIMULE_{cizelge}.json"), {}) or {} if film else {}


# --- denetim --------------------------------------------------------------------------------------------------
def denetle(islemler, plan, sahneler=None, cizelge="T1", film=None):
    """(hatalar, bayraklar) — her madde {i, op, neden}."""
    H, B = [], []
    kn = kok_nedenler(); pl = _planlar(plan); sp = _sahne_plani(sahneler)
    rep = {d.get("replik"): d for d in plan.get("diyalog") or []}
    sim = _simule(film, cizelge); sim_by = {str(o.get("no")): o for o in sim.get("oneriler") or []}
    def h(i, op, neden): H.append({"i": i, "op": op, "neden": neden})
    def b(i, op, neden): B.append({"i": i, "op": op, "neden": neden})
    if not isinstance(islemler, list): return [{"i": None, "op": None, "neden": "islemler liste değil"}], []
    for i, x in enumerate(islemler):
        if not isinstance(x, dict): h(i, None, "işlem sözlük değil"); continue
        op = x.get("op")
        if op not in OPLAR: h(i, op, f"bilinmeyen işlem: {op!r}"); continue
        if not x.get("kok_neden") or x["kok_neden"] not in kn: h(i, op, f"kok_neden veri/kok_neden.json'da yok: {x.get('kok_neden')!r}")
        if not (isinstance(x.get("bulgu"), str) and x["bulgu"].strip()): h(i, op, "bulgu kimliği yok")
        if cizelge == "T1" and op in YALNIZ_VIDEO: h(i, op, "T1'de (animatik) video işlemi yapılamaz"); continue
        p = pl.get(x.get("plan")) if x.get("plan") is not None else None
        if op in ("kirp", "uzat", "ayna", "kadraj", "hiz", "kes", "yer_tutucu", "yeniden_cek", "alternatif", "bol") and p is None:
            h(i, op, f"plan yok: {x.get('plan')!r}"); continue
        if p is not None and op not in ("yeniden_cek",) and _kilitli(p) and op not in ISTE:
            h(i, op, f"plan {p['plan']}: kullanıcının kilitli kararı değiştirilemez"); continue
        s = sp.get(x.get("plan")) or {}
        if op in ("kirp", "uzat"):
            sure = x.get("sure")
            if not isinstance(sure, (int, float)) or sure <= 0: h(i, op, "sure pozitif sayı olmalı"); continue
            if cizelge != "T1":
                bas = float(x.get("bas") or 0); klip = float((p.get("goruntu") or {}).get("klip_sn") or 8)
                if bas < (E("kullanim_bas_min_sn") or 0.3) - 1e-6 or bas + sure > klip - 0.5 + 1e-6:
                    h(i, op, f"plan {p['plan']}: pencere [{bas}, {bas + sure}] güvenli aralık dışında [≥0,3 ; ≤ klip − 0,5]")
        elif op == "sira":
            sg = x.get("sahne_grubu"); yeni = x.get("yeni_sira") or []
            grup = [q["plan"] for q in plan.get("planlar") or [] if q.get("sahne_grubu") == sg]
            if not grup: h(i, op, f"sahne grubu yok: {sg!r}"); continue
            if sorted(yeni) != sorted(grup): h(i, op, f"yeni sıra {sg} planlarının permütasyonu değil"); continue
            for eski_i, no in enumerate(grup):
                if yeni.index(no) != eski_i and (pl[no].get("etki_var") or _durum_degisir(pl[no])):
                    h(i, op, f"plan {no} durumu değiştiriyor; sahne içi sırası değişemez (Y58)")
                if yeni.index(no) != eski_i and _kilitli(pl[no]): h(i, op, f"plan {no}: kullanıcının sırası değiştirilemez")
        elif op == "jl":
            d = rep.get(x.get("replik")); t = str(x.get("tip") or "").upper(); tas = x.get("tasma_sn")
            if d is None: h(i, op, f"replik yok: {x.get('replik')!r}"); continue
            ar = E("l_kesme_aralik_sn") if t == "L" else E("j_kesme_aralik_sn") if t == "J" else None
            if ar is None: h(i, op, "tip J ya da L olmalı"); continue
            if not isinstance(tas, (int, float)) or not (ar[0] - 1e-6 <= tas <= ar[1] + 1e-6): h(i, op, f"taşma {tas} aralık dışında {ar}")
            elif t == "L":
                sira = [q["plan"] for q in plan.get("planlar") or []]
                k = sira.index(d["plan"]) + 1 if d["plan"] in sira else None
                alici = pl.get(sira[k]) if k is not None and k < len(sira) else None
                if alici is None: h(i, op, "L kesmenin üstüne bineceği plan yok")
                elif alici["sure"] < tas + (E("l_kesme_alici_plan_ek_sn") or 0.5) - 1e-6:
                    h(i, op, f"plan {alici['plan']} taşma + pay için kısa ({alici['sure']} < {tas} + {E('l_kesme_alici_plan_ek_sn')})")
        elif op == "ekran_disi":
            d = rep.get(x.get("replik")); hedef = pl.get(x.get("uzerine_plan"))
            if d is None or hedef is None: h(i, op, "replik ya da üzerine_plan yok"); continue
            hs = sp.get(hedef["plan"]) or {}; dd = hs.get("_derlenir") or {}
            konusan = d.get("karakter")
            agiz = [k.get("id") for k in (hs.get("zanaat") or {}).get("kadrajdakiler") or [] if isinstance(k, dict)
                    and k.get("id") != konusan and (k.get("konusur") or dd.get("dinleyen_agiz") == "acik")]
            if agiz or (hs.get("replik") or {}).get("id"): h(i, op, f"plan {hedef['plan']}: üstünde başka birinin ağzı oynuyor (B9)")
        elif op == "diyalog_kaydir":
            d = rep.get(x.get("replik")); sn = x.get("sn"); mx = float(E("diyalog_kaydir_max_sn") or 0.5)
            if d is None: h(i, op, f"replik yok: {x.get('replik')!r}"); continue
            if not isinstance(sn, (int, float)) or sn == 0 or abs(sn) > mx + 1e-9: h(i, op, f"kaydırma {sn} sn geçersiz (0 < |sn| ≤ {mx})")
            dp = pl.get(d.get("plan"))
            if dp is not None and _kilitli(dp) and p is None: h(i, op, f"plan {dp['plan']}: kullanıcının kilitli kararı değiştirilemez")
        elif op == "hiz":
            v = x.get("hiz"); ar = E("hiz_aralik_diyalogsuz")
            if not isinstance(v, (int, float)) or not (ar[0] <= v <= ar[1]): h(i, op, f"hız {v} aralık dışında {ar}")
            if p.get("replik"): h(i, op, f"plan {p['plan']} diyaloglu; hız değişmez")
        elif op == "kadraj":
            v = x.get("oran", x.get("yakinlastirma"))
            if not isinstance(v, (int, float)) or v < 0 or v > E("yeniden_kadraj_max"): h(i, op, f"yeniden kadraj {v} > {E('yeniden_kadraj_max')}")
        elif op == "ayna":
            if (s.get("_derlenir") or {}).get("ayna_yasak", True): h(i, op, f"plan {p['plan']}: ayna yasak (yazı, yara ya da asimetri)")
        elif op == "kart":
            if x.get("kart_tur") not in KART_TURLERI: h(i, op, f"kart türü geçersiz: {x.get('kart_tur')!r}")
            if not (isinstance(x.get("metin"), str) and x["metin"].strip()): h(i, op, "kart metni boş")
            if x.get("plan") is not None and p is None and pl.get(x["plan"]) is None: h(i, op, "kartın planı yok")
        elif op == "kes":
            ref = str(x.get("simule") or "")
            if "kesici" in str(x.get("bulgu")) or ref:
                m = re.search(r"#(\w+)$", ref)
                o = sim_by.get(m.group(1)) if m else None
                if o is None: h(i, op, "kesici önerisinin simülasyon kaydı yok (kurgu_denetim --kesme-simule)")
                elif not o.get("gecti"): h(i, op, f"öneri {o.get('no')} simülasyonda HATA verdi: {'; '.join(o.get('hatalar') or [])[:160]}")
        elif op == "ortu":
            if pl.get(x.get("kaynak_plan")) is None: h(i, op, "örtü kaynak planı yok")
            ar = x.get("araya") or []
            if len(ar) != 2 or any(pl.get(a) is None for a in ar): h(i, op, "araya [önceki, sonraki] plan çifti olmalı")
            ku = x.get("kullanim") or {}
            if float(ku.get("sure") or 0) < 1.0: b(i, op, "örtü süresi taban 1,0 sn'nin altında (ortu_min_sn)")
        elif op == "yeniden_cek":
            sk = x.get("sifir_kredi") or {}
            if not (isinstance(sk.get("gerekce"), str) and sk["gerekce"].strip()):
                h(i, op, "0 kredi kuralı: sifir_kredi.gerekce olmadan yeniden çekim önerilemez (D-31)")
        elif op in ISTE:
            if not (x.get("gereksinim") or x.get("istek") or x.get("bilgi") or x.get("sahne")): h(i, op, "isteğin içeriği boş")
    # kesme oranı (İ-6): simülasyondan temiz geçenlerin ≥ %50'si uygulanmalı
    temiz = [o for o in sim.get("oneriler") or [] if o.get("gecti")]
    if temiz and sim.get("tur") is not None and not sim.get("uygulandi"):
        uyg = {str(re.search(r"#(\w+)$", str(x.get("simule") or "")).group(1)) for x in islemler
               if isinstance(x, dict) and x.get("op") in ("kes", "kes_sahne_iste") and re.search(r"#(\w+)$", str(x.get("simule") or ""))}
        oran_min = (E("kesme_turu_oneri") or {}).get("uygulama_orani_min", 0.5)
        if len([o for o in temiz if str(o.get("no")) in uyg]) < math.ceil(oran_min * len(temiz) - 1e-9):
            h(None, "kes", f"kesme turu: simülasyondan temiz geçen {len(temiz)} önerinin en az %{int(oran_min * 100)}'i uygulanmalı "
                          f"(uygulanan {len(uyg & {str(o.get('no')) for o in temiz})})")
    return H, B


def _ofset_sabitle(plan):
    """T2 diyaloğu (plan_kurgu) plan_ofset taşımaz; yeniden_zamanla repliği planın başına çekmesin diye planın başına göre ofset yazılır."""
    bas = {q.get("plan"): q.get("cizelge_bas") for q in plan.get("planlar") or []}
    for d in plan.get("diyalog") or []:
        if d.get("plan_ofset") is None and d.get("cizelge_bas") is not None and bas.get(d.get("plan")) is not None:
            d["plan_ofset"] = round(float(d["cizelge_bas"]) - float(bas[d["plan"]]), 4)


def _durum_degisir(p):
    d = p.get("durum_ozet") or {}
    return bool(d) and d.get("bas") != d.get("bit")


# --- uygulama ---------------------------------------------------------------------------------------------------
def uygula(plan, islemler, sahneler=None):
    """İşlemleri plan sözlüğüne uygular (yerinde). *_iste ve yeniden_cek planı değiştirmez. Değişen plan listesini döndürür."""
    pl = _planlar(plan); degisen = set()
    for x in islemler:
        op = x.get("op"); p = pl.get(x.get("plan"))
        if op in ("kirp", "uzat") and p:
            p["sure"] = float(x["sure"]); g = p.setdefault("goruntu", {})
            g.setdefault("kullanim", {})["sure"] = float(x["sure"])
            if x.get("bas") is not None: g["kullanim"]["bas"] = float(x["bas"])
            g["kullanim_kaynak"] = "kurgucu"; degisen.add(p["plan"])
        elif op == "sira":
            grup = [q for q in plan["planlar"] if q.get("sahne_grubu") == x["sahne_grubu"]]
            yer = [plan["planlar"].index(q) for q in grup]
            sirali = [pl[n] for n in x["yeni_sira"]]
            for k, q in zip(yer, sirali): plan["planlar"][k] = q
            degisen |= set(x["yeni_sira"])
        elif op == "jl":
            for d in plan.get("diyalog") or []:
                if d.get("replik") == x["replik"]: d["jl"] = {"tip": str(x["tip"]).upper(), "tasma_sn": float(x["tasma_sn"])}
        elif op == "ekran_disi":
            for d in plan.get("diyalog") or []:
                if d.get("replik") == x["replik"]:
                    d.update(plan=x["uzerine_plan"], ekran_disi=True, gorunen_konusan=False, plan_ofset=float(x.get("ofset") or 0))
        elif op == "diyalog_kaydir":
            for d in plan.get("diyalog") or []:
                if d.get("replik") == x["replik"]:
                    d["plan_ofset"] = round(float(d.get("plan_ofset") or 0) + float(x["sn"]), 4)
                    d["kaydirma_sn"] = round(float(d.get("kaydirma_sn") or 0) + float(x["sn"]), 4)
                    if d.get("cizelge_bas") is not None: d["cizelge_bas"] = round(float(d["cizelge_bas"]) + float(x["sn"]), 4)
                    if d.get("plan") is not None: degisen.add(d["plan"])
        elif op == "hiz" and p:
            p["goruntu"]["hiz"] = float(x["hiz"]); p["sure"] = round(float(p["sure"]) / float(x["hiz"]), 4); degisen.add(p["plan"])
        elif op == "ayna" and p: p["goruntu"]["ayna"] = True; degisen.add(p["plan"])
        elif op == "kadraj" and p: p["goruntu"]["kadraj_kirpma"] = float(x.get("oran", x.get("yakinlastirma"))); degisen.add(p["plan"])
        elif op == "yer_tutucu" and p: p["goruntu"].update(tur="yer_tutucu", dosya=None); degisen.add(p["plan"])
        elif op == "kes" and p:
            plan["planlar"] = [q for q in plan["planlar"] if q is not p]
            plan["diyalog"] = [d for d in plan.get("diyalog") or [] if d.get("plan") != p["plan"]]
            plan.setdefault("kesilenler", []).append(p["plan"]); pl.pop(p["plan"], None)
        elif op == "kart":
            anah = (x.get("kart_tur"), x.get("plan"), x.get("metin"))
            if not any((k.get("tur"), k.get("plan"), k.get("metin")) == anah for k in plan.get("kartlar") or []):
                plan.setdefault("kartlar", []).append({"tur": x["kart_tur"], "metin": x["metin"], "plan": x.get("plan"),
                                                        "ofset": float(x.get("ofset") or 0), "sure": float(x.get("sure") or 3.0),
                                                        "ust_uste": x.get("ust_uste", True)})
        elif op == "ortu":
            a, bno = x["araya"]; k = next((j for j, q in enumerate(plan["planlar"]) if q["plan"] == a), None)
            kp = pl.get(x["kaynak_plan"])
            if k is not None and kp:
                yeni = copy.deepcopy(kp); yeni["plan"] = round(a + 0.5, 1); yeni["ortu"] = {"kaynak_plan": kp["plan"]}
                yeni["sure"] = float((x.get("kullanim") or {}).get("sure") or 1.0); yeni["replik"] = None; yeni["serit"] = []
                yeni["goruntu"]["kullanim"] = dict(x.get("kullanim") or {}); yeni["goruntu"]["kullanim_kaynak"] = "kurgucu"
                plan["planlar"].insert(k + 1, yeni); pl[yeni["plan"]] = yeni
    return sorted(degisen, key=lambda v: float(v))


def duzen_uygula(plan, islemler, sahneler=None):
    """Kalıcı katmandaki işlemleri yeniden uygular; artık geçersiz olan işlem atlanır (sessiz değil: plan['duzen_atlanan'])."""
    gecerli, atlanan = [], []
    for x in islemler:
        if x.get("op") in ISTE or x.get("op") == "yeniden_cek": continue
        hs, _ = denetle([x], plan, sahneler, plan.get("cizelge", "T1"))
        hs = [h for h in hs if "simülasyon" not in h["neden"] and "kesme turu" not in h["neden"]]
        if hs: atlanan.append({"islem": x, "neden": hs[0]["neden"]}); continue
        uygula(plan, [x], sahneler); gecerli.append(x)
    if atlanan: plan["duzen_atlanan"] = atlanan
    return gecerli


# --- dosya akışı ------------------------------------------------------------------------------------------------
def kararlar_bul(film, cizelge, tur, asama=None):
    if asama == "A16n":
        p = os.path.join(film, "NOT_CEVAPLARI.json")
        if os.path.isfile(p): return p
    p = os.path.join(film, "KURGU", f"KURGU_KARARLARI_{cizelge}_t{tur}.json")
    if os.path.isfile(p): return p
    ad = sorted(glob.glob(os.path.join(film, "KURGU", f"KURGU_KARARLARI_{cizelge}_t*.json")),
                key=lambda x: int(re.search(r"_t(\d+)\.json$", x).group(1)))
    return ad[-1] if ad else None


KARAR_OP = {"kirp": "kirp", "uzat": "uzat", "sira": "sira", "kes": "kes", "lj": "jl", "jl": "jl", "yeniden_cek": "yeniden_cek",
            "ekran_disi": "ekran_disi", "kart": "kart", "hiz": "hiz", "ayna": "ayna"}


def karar_cevir(x):
    """Şablondaki kısa biçim (rapor.json `kararlar[{madde, tur, plan, zaman, deger, kok_neden?}]`) → [KU2] §4.5.6 işlemi."""
    t = x.get("tur"); d = x.get("deger"); op = KARAR_OP.get(t)
    if t == "tepki": op = "ortu" if isinstance(d, dict) and d.get("kaynak_plan") else "yeni_plan_iste"
    out = {"op": op or t, "plan": x.get("plan"), "kok_neden": x.get("kok_neden"), "bulgu": x.get("bulgu") or x.get("madde"),
           "_kaynak_bicim": "kararlar"}
    if isinstance(d, dict): out.update({k: v for k, v in d.items() if k not in out or out[k] is None})
    elif op in ("kirp", "uzat") and isinstance(d, (int, float)): out["sure"] = d
    elif op == "sira" and isinstance(d, list): out["yeni_sira"] = d
    elif op == "hiz" and isinstance(d, (int, float)): out["hiz"] = d
    elif op == "yeni_plan_iste" and d: out["gereksinim"] = str(d)
    return out


def islemleri_oku(yol):
    k = ortak.json_oku(yol)
    if isinstance(k, list): return k, {}
    if not isinstance(k, dict): raise KurguHatasi(f"karar dosyası okunamadı: {yol}")
    if k.get("islemler") is None and isinstance(k.get("kararlar"), list):
        return [karar_cevir(x) for x in k["kararlar"] if isinstance(x, dict)], k
    return k.get("islemler") or [], k


def _istek_kuyrugu(film, cizelge, tur, istekler, asama):
    if not istekler: return None
    ortak.atomik_yaz(os.path.join(film, "KURGU", f"ISTEKLER_{cizelge}_t{tur}.json"),
                     {"_surum": 1, "cizelge": cizelge, "tur": tur, "istekler": istekler})
    yaz = []
    for x in istekler:
        sahip = x.get("sahip") or ("yonetmen" if x["op"] == "yeni_plan_iste" else "hikaye-yazari" if x["op"] in ("kopru_replik_iste", "kes_sahne_iste")
                                   else "ses-tasarimcisi")
        if sahip not in ("yonetmen", "hikaye-yazari"): continue
        konum = {}
        ar = x.get("araya") or []
        if x.get("plan") is not None or ar: konum["plan"] = int(x.get("plan") or ar[0])
        if isinstance(x.get("sahne"), str) and re.fullmatch(r"S\d{2,}", x["sahne"]): konum["sahne"] = x["sahne"]
        if not konum: continue
        yaz.append({"konum": konum, "kapi": "AI" if cizelge == "T1" else "KI", "madde": x["op"], "kok_neden": x["kok_neden"],
                    "yazar": sahip, "oneri": str(x.get("gereksinim") or x.get("istek") or x.get("bilgi") or x.get("sahne")), "tur": int(tur)})
    if yaz:
        try:
            import kuyruk
            return kuyruk.yaz_ekle(film, yaz, asama or ("A12" if cizelge == "T1" else "A16"))
        except Exception as e: return {"hata": str(e)}
    return None


def _yeniden_cek(film, cizelge, tur, ops):
    if not ops: return None
    import kuyruk
    m = [{"plan": int(x["plan"]), "tur": "gorsel" if cizelge == "T1" else "video", "kaynak_kapi": "AI" if cizelge == "T1" else "KI",
          "kok_neden": x["kok_neden"], "seviye": x.get("seviye") or "ORTA", "cozum": "yeniden_cek",
          "duzeltme": x.get("istek") or x.get("duzeltme"), "sifir_kredi": dict(x.get("sifir_kredi") or {}, denendi=True),
          "kaynak_rapor": f"KURGU/KURGU_KARARLARI_{cizelge}_t{tur}.json"} for x in ops]
    return kuyruk.ekle(film, m, kapi_tur=tur)


SES_ISTEKLERI = os.path.join("KURGU", "SES_ISTEKLERI.json")


def _ses_istekleri_oku(film):
    v = ortak.json_oku(os.path.join(film, SES_ISTEKLERI), {}) or {}
    return v, [m for m in v.get("islemler") or [] if isinstance(m, dict) and not m.get("yapildi")]


def ses_istekleri(film, plan, sahneler, islemler):
    """ses_karar'ın ekran_disi istekleri (KURGU/SES_ISTEKLERI.json, ses_karar ekran_disi_tts basamağı) → ekran_disi işlemleri.
    Kurgucu aynı replik için kendisi karar verdiyse istek onun kararıyla karşılanır. Hedef plan verilmemişse konuşanın planından sonraki,
    sonra önceki planlar (aynı sahne grubu önce) sırayla denenir; B9'dan (başka ağız) geçen ilk plan seçilir. → (işlemler, maddeler, bayraklar)"""
    _, bekleyen = _ses_istekleri_oku(film)
    if not bekleyen: return [], [], []
    kurgucu = {x.get("replik") for x in islemler if isinstance(x, dict) and x.get("op") == "ekran_disi"}
    rep = {d.get("replik"): d for d in plan.get("diyalog") or []}
    sira = [q.get("plan") for q in plan.get("planlar") or []]
    sg = {q.get("plan"): q.get("sahne_grubu") for q in plan.get("planlar") or []}
    ops, maddeler, bay = [], [], []
    for m in bekleyen:
        rid = m.get("replik"); d = rep.get(rid)
        if rid in kurgucu: maddeler.append((m, "kurgucu")); continue
        if d is None: bay.append({"i": None, "op": "ekran_disi", "neden": f"SES_ISTEKLERI: replik çizelgede yok: {rid!r}"}); continue
        kaynak = d.get("plan") if d.get("plan") is not None else m.get("plan")
        if m.get("uzerine_plan") is not None: adaylar = [m["uzerine_plan"]]
        else:
            k = sira.index(kaynak) if kaynak in sira else -1
            yakin = sorted((j for j in range(len(sira)) if j != k), key=lambda j: (abs(j - k), j < k)) if k >= 0 else range(len(sira))
            adaylar = [sira[j] for j in yakin if sg.get(sira[j]) == sg.get(kaynak)] + [sira[j] for j in yakin if sg.get(sira[j]) != sg.get(kaynak)]
        secilen = None
        for a in adaylar:
            op = {"op": "ekran_disi", "replik": rid, "uzerine_plan": a, "kok_neden": m.get("kok_neden") or "dudak_kayma",
                  "bulgu": f"SES_ISTEKLERI#{rid}", "_kaynak": SES_ISTEKLERI}
            if not denetle([op], plan, sahneler, plan.get("cizelge", "T2"))[0]: secilen = op; break
        if secilen: ops.append(secilen); maddeler.append((m, secilen["uzerine_plan"]))
        else: bay.append({"i": None, "op": "ekran_disi", "neden": f"SES_ISTEKLERI {rid}: ağzı başka kimsenin oynamadığı plan bulunamadı (B9)"})
    return ops, maddeler, bay


def _ses_istekleri_isaretle(film, maddeler, surum):
    if not maddeler: return
    v, _ = _ses_istekleri_oku(film)
    for m, hedef in maddeler:
        for x in v.get("islemler") or []:
            if x.get("replik") == m.get("replik") and not x.get("yapildi"):
                x.update(yapildi=True, uygulandi={"uzerine_plan": None if hedef == "kurgucu" else hedef, "karar": "kurgucu" if hedef == "kurgucu"
                                                   else "kurgu_uygula", "surum": surum})
                break
    ortak.atomik_yaz(os.path.join(film, SES_ISTEKLERI), v)


def calistir(film, cizelge="T1", tur=1, kararlar=None, kuru=False, asama=None):
    film = os.path.abspath(film)
    import zaman_cizelgesi_t1 as t1
    yol = kararlar or kararlar_bul(film, cizelge, tur, asama)
    if yol and os.path.isfile(yol): islemler, ust = islemleri_oku(yol)
    elif cizelge != "T1" and _ses_istekleri_oku(film)[1]: islemler, ust, yol = [], {}, os.path.join(film, SES_ISTEKLERI)
    else: raise FileNotFoundError("kurgu karar dosyası yok")
    cizelge = ust.get("asama") if ust.get("asama") in ("T1", "T2", "T3") else cizelge
    plan, pyol, n = t1.plan_oku(film, cizelge)
    if plan is None: raise FileNotFoundError(f"KURGU_PLANI_{cizelge} yok")
    sahneler = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
    ses_ops, ses_maddeler, ses_bay = ses_istekleri(film, plan, sahneler, islemler) if cizelge != "T1" else ([], [], [])
    islemler = list(islemler) + ses_ops
    H, B = denetle(islemler, plan, sahneler, cizelge, film)
    B = B + ses_bay
    sonuc = {"karar_dosyasi": os.path.relpath(yol, film), "cizelge": cizelge, "temel_surum": n, "hatalar": H, "bayraklar": B,
             "ses_istekleri": [{"replik": m.get("replik"), "uzerine_plan": h} for m, h in ses_maddeler]}
    if kuru or H: return (1 if H else 0), sonuc
    yeni = copy.deepcopy(plan)
    _ofset_sabitle(yeni)
    degisen = uygula(yeni, islemler, sahneler)
    t1.yeniden_zamanla(yeni)
    if cizelge == "T1": t1.olcumler(yeni)
    yeni["kurgu_surumu"] = n + 1
    yeni["_uretim"] = dict(plan.get("_uretim") or {}, arac_surum=SURUM, zaman=t1.simdi(), sonuc="GEC",
                           girdi_imza=t1.sha(yol))
    yeni["onceki_surum"] = n; yeni["degisen_planlar"] = degisen
    hedef = t1.plan_yolu(film, cizelge, n + 1)
    ortak.atomik_yaz(hedef, yeni)
    dz_yol = os.path.join(film, "KURGU", f"KURGU_DUZEN_{cizelge}.json")
    dz = ortak.json_oku(dz_yol, {}) or {"_surum": 1, "cizelge": cizelge, "islemler": []}
    for x in islemler:
        if x.get("op") in ISTE or x.get("op") == "yeniden_cek": continue
        dz["islemler"].append(dict(x, _kaynak=os.path.relpath(yol, film), _tur=tur))
    ortak.atomik_yaz(dz_yol, dz)
    sonuc["istek"] = _istek_kuyrugu(film, cizelge, tur, [x for x in islemler if x.get("op") in ISTE], asama)
    sonuc["yeniden_cek"] = _yeniden_cek(film, cizelge, tur, [x for x in islemler if x.get("op") == "yeniden_cek"])
    sim_yol = os.path.join(film, "_RAPOR", f"KESME_SIMULE_{cizelge}.json")
    sim = ortak.json_oku(sim_yol)
    if isinstance(sim, dict) and any(x.get("op") in ("kes", "kes_sahne_iste") for x in islemler):
        sim["uygulandi"] = os.path.relpath(yol, film); ortak.atomik_yaz(sim_yol, sim)
    _ses_istekleri_isaretle(film, ses_maddeler, os.path.relpath(hedef, film).replace("\\", "/"))
    sonuc.update(yeni_surum=os.path.relpath(hedef, film), degisen=degisen)
    ortak.atomik_yaz(os.path.join(film, "_RAPOR", f"KURGU_UYGULA_{cizelge}_t{tur}.json"),
                     {"_surum": 1, "_uretim": {"asama": asama, "arac_surum": SURUM, "zaman": t1.simdi(), "sonuc": "GEC", "ortam": t1.ortam(),
                                               "gorev": os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None,
                                               "girdi_imza": t1.sha(yol), "esik_surum": None}, **sonuc})
    return 0, sonuc


def main(argv=None):
    ap = argparse.ArgumentParser(description="Kurgu işlem listesi doğrulama/uygulama.")
    ap.add_argument("--kuru"); ap.add_argument("--uygula", action="store_true"); ap.add_argument("--kararlar")
    ap.add_argument("--cizelge", default=None); ap.add_argument("--tur", type=int); ap.add_argument("--film"); ap.add_argument("--saglayici")
    o = ap.parse_args(argv)
    film = o.film or os.environ.get("YZ_FILM_FILM")
    if not film or not os.path.isdir(film): print("!! --film <film klasörü> gerekli."); return 4
    import zaman_cizelgesi_t1 as t1
    g = t1.gorev_baglami(o.tur)
    cizelge = o.cizelge or ("T1" if (g.get("asama") or "A12") == "A12" else "T2")
    try:
        kod, s = calistir(film, cizelge, g["tur"], o.kuru or o.kararlar, kuru=bool(o.kuru), asama=g.get("asama"))
    except FileNotFoundError as e: print("!! " + str(e)); return 2
    except KurguHatasi as e: print("!! " + str(e)); return 1
    print(json.dumps({k: s.get(k) for k in ("hatalar", "bayraklar", "yeni_surum", "degisen")}, ensure_ascii=False)[:4000])
    return kod


if __name__ == "__main__":
    sys.exit(main())
