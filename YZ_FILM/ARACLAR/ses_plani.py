"""SES PLANI — kâğıt ses aşamaları (TASARIM §1.3 A06s/A08, §2.2, §6.6, §7.2 S0; [SM2] §4.2 SA1–SA4, §4.5, §4.7.1).
film.py görevi olarak çağrılır: "python ses_plani.py <alt komut> --film <film>" (YZ_FILM_GOREV = görev klasörü; rapor yolu ve tur oradan).

Alt komutlar:
  --profil-denetle   (A06s) HIKAYE.json + _SES/SES_PROFILLERI.json → _RAPOR/S0_PROFIL_t<n>.json (kapı S0, birim = karakter):
                     konuşan her karakterin profili tam (cinsiyet, yaş bandı, aksan, perde, tını, tempo, enerji, veo_ses_tarifi,
                     ses_etiketi_tr; H), S0.5 tarif kuralları (≤ 12 kelime, tını + cinsiyet + aksan, yaş/filtre sözcüğü yok; H; sıra B),
                     aksan 'neutral' B, aynı cinsiyet + yaş bandında perde/tını ayrışmıyor B, evrende kilitli ses değişmiş H,
                     yaratığa dönüştürücü/Veo tarifi H, figüran yalnız 'veo_ham' kuralıyla, ad_telaffuz yok B.
  --taslak           (A08, kod önerisi) SAHNELER v2 + DUNYA_DEFTERI + HIKAYE + profiller + evren mekân sesi + veri/efekt_sozlugu →
                     _SES/SES_<S>.taslak.json (sahne grubu başına): diyalog yolu (_derlenir.agiz_gorunur tam/kısmi → veo_donustur,
                     yok → tts, figüran → veo_ham, aktif 'yol_kurali' dersi), fiziksel/mikro adım başına efekt olayı (fiil → efekt
                     sözlüğü; eşleşmeyen fiziksel adım 'sessiz_adim' + boş neden = ses-tasarimcisi doldurur), tek yatak + defter/zaman
                     katmanları (aynı mekân ve kesintisiz zamanda önceki yatak), oda yanıtı, çapraz geçiş, flow_sound
                     ("Sound: <2–3 olay>, <yatak>. No music.", ≤ 12 kelime), vuruşlardan sessizlik önerileri.
  --denetle --tum    (A08 S0) _SES/SES_*.json (ses-tasarimcisi·tasarim çıktıları) SAHNELER'e uygulanmış görünümde S0.1–S0.21
                     + muzik.py kâğıt maddeleri (S0.14–S0.18) → _RAPOR/S0_FILM.json. HATA yoksa tasarım SAHNELER.json'a yazılır
                     (zanaat.ses, sahne_gruplari.<S>.ses, _derlenir.{ton_fiili_en, seviye, muzik_ipucu}); HATA'da SAHNELER değişmez,
                     eşlenebilen maddeler KUYRUK/YENIDEN_YAZ'a (yazar ses-tasarimcisi). Kod _derlenir'e yazdığı için
                     _YONETMEN/DERLENIR_IMZA.json tazelenir (plan_birlestir.imza_yaz; istem_derle ile aynı yol) ve
                     _SES/SES_TASARIMI.md (insan için özet) yazılır. Profil denetimi SES_KADROSU.md yoksa özetini yazar.
  --denetle --sahne <S>   tek sahne grubu (SubagentStop denetimi) → _RAPOR/S0_<S>.json; SAHNELER'e yazmaz.
Ortak seçenekler: --film <ad|yol> (zorunlu) · --tur N (görev klasörü yoksa)
Kodda: ses_tanitim_kurali(sahneler, gizem=()) → [{plan, karakter}] (S0.3 ve Y59 aynı fonksiyon) ·
       dinleyen_agiz_kurali(plan) → bool (S0.2 ve Y35) · zaman_cizelgesi(sahneler) → [(plan, bas, bit)] · uygula(plan, ses_dosyalari)
S0.19 (evren ses kaydı) ve S0.20 (telaffuz testi) A10b/A10c'den sonra ölçülür; o raporlar yokken bu maddeler raporun 'ertelenen'
listesinde durur (geçmiş sayılmaz, yazılı kalır).
Çıkış kodları: 0 rapor/taslak yazıldı (kapı sonucu raporda; film.py okur) · 1 girdi yok ya da bozuk · 4 ORTAM (YOLLAR.json yok,
               SAHNELER v1) · kullanım hatası 4.
"""
import os, re, sys, json, glob
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi
import istem_denetim_ses as ids

SURUM = "ses_plani 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
SES = "_SES"
PLAN_SES_ALANLARI = ("diyalog", "efektler", "flow_sound", "sessizlik", "dis_katman_db")
GRUP_SES_ALANLARI = ("yatak", "oda_yaniti", "gecis", "kalabalik")
YOLLAR = ("veo_donustur", "tts", "veo_ham")
IC_MEKAN = ("kulube", "oda", "ev", "salon", "mutfak", "ahir", "han", "tapinak", "ic", "kiler", "zindan", "meyhane", "kilise")
ZEMIN_EN = {"kar": "snow", "ahsap": "wooden boards", "ahsap_tahta": "wooden boards", "tahta": "wooden boards", "tas": "stone",
            "toprak": "earth", "cimen": "grass", "kum": "sand", "buz": "ice", "camur": "mud", "cakil": "gravel", "kaya": "rock"}
HAVA_EN = {"kar": "wind over snow", "yagmur": "steady rain", "ruzgar": "wind gusting", "firtina": "a storm howling",
           "sis": "still, damp air"}
EFEKT_EN = {"ayak": "footsteps on {zemin}", "kumas": "cloth rustling", "nesne_temas": "a soft touch", "nesne_birakma": "something set down",
            "kapi": "a door creaking", "ates": "a flame flaring", "nefes": "a soft breath", "gulus": "a short laugh",
            "kuyruk": "a tail sweeping {zemin}", "oturma": "a quiet creak"}
EFEKT_ONCELIK = ("kapi", "ates", "nesne_temas", "nesne_birakma", "ayak", "kuyruk", "oturma", "kumas", "nefes", "gulus")
KOK_NEDEN = {"S0.7": "efekt_eksik", "S0.10": "ambiyans_zipladi", "S0.11": "ambiyans_zipladi", "S0.18": "muzik_motifsiz"}


# --- genel yardımcılar -----------------------------------------------------------------------------------------------
def E_():
    return ids.esikler_()


def e(ad, v=None):
    x = E_().get(ad) if hasattr(E_(), "get") else None
    return v if x is None else x


def orta(ar, v):
    return (ar[0] + ar[1]) / 2.0 if isinstance(ar, (list, tuple)) and len(ar) == 2 else v


def m(madde, seviye, plan=None, birim=None, **k): return ids.m(madde, seviye, plan, birim, **k)


def gorev_baglami(tur=None, asama=None):
    g = ortak.json_oku(os.path.join(os.environ.get("YZ_FILM_GOREV") or "", "GOREV.json"), {}) or {}
    return {"id": g.get("id"), "tur_no": int(tur or g.get("tur_no") or 1), "asama": g.get("asama") or asama, "rapor": g.get("rapor")}


def rapor_yaz(film, g, kapsam, olc, varsayilan, birimler=(), ek=None):
    yol = os.path.join(film, g["rapor"]) if g.get("rapor") else os.path.join(film, varsayilan.format(tur=g["tur_no"]))
    r = kapi.rapor_kur("S0", kapsam, olc, tur=g["tur_no"], asama=g["asama"], gorev=g["id"], arac_surum=SURUM,
                       birimler=list(birimler), ek=ek)
    h = kapi.dogrula(r)
    if h: raise kapi.RaporHatasi(h)
    ortak.atomik_yaz(yol, r)
    print(f"S0 {kapsam}: {r['sonuc']} · HATA {len(r['hatalar'])} · BAYRAK {len(r['bayraklar'])} → {os.path.relpath(yol, film)}")
    return yol, r


def hikaye_oku(film): return ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}


def karakterler(h):
    k = h.get("karakterler") or {}
    return k if isinstance(k, dict) else {x.get("id"): x for x in k if isinstance(x, dict)}


def yaratiklar(h): return {kid for kid, k in karakterler(h).items() if (k or {}).get("rol") == "yaratik" or (k or {}).get("tur") == "yaratik"}


def konusmaz(h): return yaratiklar(h) | {kid for kid, k in karakterler(h).items() if (k or {}).get("konusmaz")}


def figuranlar(h, prof):
    f = {kid for kid, k in karakterler(h).items() if (k or {}).get("rol") == "figuran"}
    return f | {kid for kid, p in prof.items() if p.get("yol") == "veo_ham"}


def hikaye_sahneleri(h): return {s.get("id"): s for s in h.get("sahneler") or [] if isinstance(s, dict)}


def evren_json(h, *p):
    try:
        import evren
        seri = h.get("evren")
        return ortak.json_oku(evren.seri_yolu(seri, *p)) if seri else None
    except Exception:
        return None


def ogrenilen():
    try: return ortak.json_oku(os.path.join(ortak.yollar()["veri_kok"], "BILGI", "KURALLAR_OGRENILEN.json"), {}) or {}
    except ortak.YolYok: return {}


def sahneler_v2(film):
    """(plan sözlüğü, hata kodu). v1 dosyası 4."""
    p = ortak.json_oku(os.path.join(film, "SAHNELER.json"))
    if not isinstance(p, dict): print("!! SAHNELER.json yok ya da bozuk"); return None, HATA
    if int(p.get("_surum", 1) or 1) < 2: print("!! SAHNELER.json v1; ses_plani v2 dosyası ister"); return None, ORTAM
    return p, BITTI


def plan_listesi(plan):
    ps = [s for s in plan.get("sahneler") or [] if isinstance(s, dict)]
    return sorted(ps, key=lambda s: (s.get("sira") if s.get("sira") is not None else s.get("no") or 0))


def grup_adi(s): return (s.get("zanaat") or {}).get("sahne_grubu")


def gruplar(plan):
    """{S: [plan, …]} sahne_gruplari sırasıyla (yoksa planlardaki ilk görünüş sırası)."""
    ps = plan_listesi(plan); out = {}
    for S in plan.get("sahne_gruplari") or {}: out[S] = []
    for s in ps: out.setdefault(grup_adi(s) or "_grupsuz", []).append(s)
    return {k: v for k, v in out.items() if v or k in (plan.get("sahne_gruplari") or {})}


def plan_sure(s):
    d = s.get("_derlenir") or {}; k = s.get("kullanim") or {}; z = s.get("zanaat") or {}
    for v in (d.get("sure_sn"), k.get("sure"), z.get("klip_sn"), (s.get("uretim") or {}).get("klip_sn")):
        if isinstance(v, (int, float)) and v > 0: return float(v)
    return 8.0


def zaman_cizelgesi(sahneler):
    """[(plan, bas, bit)] kurgu sırasıyla (T0: kullanım süresi; bilgi amaçlı, kesin zaman zaman_cizelgesi.py'dedir)."""
    t, out = 0.0, []
    for s in sorted(sahneler, key=lambda s: (s.get("sira") if s.get("sira") is not None else s.get("no") or 0)):
        d = plan_sure(s); out.append((s, t, t + d)); t += d
    return out


def klip_to_film(s, bas, t_klip):
    k0 = float((s.get("kullanim") or {}).get("bas") or 0.0)
    return bas + max(0.0, float(t_klip) - k0)


def adimlar(s): return [a for a in (s.get("zanaat") or {}).get("eylem_zinciri") or [] if isinstance(a, dict)]


def konusur_mu(s):
    return bool((s.get("replik") or {}).get("metin")) or any(a.get("tur") == "konusma" for a in adimlar(s))


def replik_pencereleri(s):
    """Klip zamanında [(R, bas, bit)]: _derlenir.replik_zaman ({R: [b, s]} ya da {bas, bit}) ya da konuşma adımları."""
    rz = (s.get("_derlenir") or {}).get("replik_zaman") or {}; out = []
    if isinstance(rz, dict) and "bas" in rz and "bit" in rz:
        out.append(((s.get("replik") or {}).get("id"), float(rz["bas"]), float(rz["bit"])))
    elif isinstance(rz, dict):
        for R, v in rz.items():
            if isinstance(v, (list, tuple)) and len(v) == 2: out.append((R, float(v[0]), float(v[1])))
    if not out:
        for a in adimlar(s):
            if a.get("tur") == "konusma" and a.get("bas") is not None and a.get("bit") is not None:
                out.append((a.get("replik"), float(a["bas"]), float(a["bit"])))
    return out


def ses_of(s): return (s.get("zanaat") or {}).get("ses") or {}


# --- kurallar (tek fonksiyon; plan_denetim Y35/Y59 da bunları çağırır) -------------------------------------------------
def dinleyen_agiz_kurali(s):
    """S0.2 / Y35: ekran dışı ses varken kadrajdakilerin ağzı kapalı (_derlenir.dinleyen_agiz == 'kapali')."""
    if not (s.get("zanaat") or {}).get("ekran_disi_ses"): return True
    return (s.get("_derlenir") or {}).get("dinleyen_agiz") == "kapali"


def ses_tanitim_kurali(sahneler, gizem=()):
    """S0.3 / Y59: TTS kaynaklı ekran dışı ses, karakter daha önce ekranda konuşurken duyulduktan sonra gelir.
    gizem: istisna karakterler (gizem_sesi). Dönüş: ihlaller [{plan, karakter}]."""
    duyuldu, out = set(), []
    for s, _, _ in zaman_cizelgesi(sahneler):
        z = s.get("zanaat") or {}; rep = s.get("replik") or {}
        eds = z.get("ekran_disi_ses") or {}
        kadraj = {k.get("id") for k in z.get("kadrajdakiler") or [] if isinstance(k, dict)}
        aday = []
        if eds and (eds.get("kaynak") == "tts" or ((eds.get("kaynak") or "").startswith("tts"))):
            aday.append((eds.get("karakter"), eds.get("gizem_sesi")))
        if rep.get("metin") and (s.get("_derlenir") or {}).get("agiz_gorunur") == "yok" and rep.get("karakter") not in kadraj:
            aday.append((rep.get("karakter"), rep.get("gizem_sesi")))
        for kar, giz in aday:
            if kar and kar not in duyuldu and not giz and kar not in gizem: out.append({"plan": s.get("no"), "karakter": kar})
        if rep.get("metin") and (s.get("_derlenir") or {}).get("agiz_gorunur") in ("tam", "kismi"): duyuldu.add(rep.get("karakter"))
    return out


def yol_onerisi(s, h, prof, kurallar=()):
    """(yol, yol_neden): kod önerisi (§2.2 karar 3)."""
    rep = s.get("replik") or {}; kar = rep.get("karakter")
    if not konusur_mu(s): return None, None
    for k in kurallar:
        ko = k.get("kosul") or {}
        if all(((s.get("_derlenir") or {}).get(a) if a in ("agiz_gorunur",) else rep.get(a)) == v for a, v in ko.items()) \
                and k.get("yol") in YOLLAR:
            return k["yol"], f"ders:{k.get('id')}"
    if kar in figuranlar(h, prof): return "veo_ham", None
    ag = (s.get("_derlenir") or {}).get("agiz_gorunur")
    return ("veo_donustur" if ag in ("tam", "kismi") else "tts"), None


def beklenen_yol(s, h, prof, kurallar=()):
    y, _ = yol_onerisi(s, h, prof, kurallar)
    return y


# --- A06s: profil denetimi --------------------------------------------------------------------------------------------
def profil_olcumleri(h, prof, E=None, evren_sesleri=None):
    """[ölçüm] (birim = karakter)."""
    E = E or E_(); out = []
    kar = karakterler(h); sus = konusmaz(h); yar = yaratiklar(h)
    konusan = []
    for r in h.get("replikler") or []:
        k = (r or {}).get("karakter")
        if k and k not in konusan and k not in sus: konusan.append(k)
    if not prof: out.append(m("profil_dosyasi", "HATA", oneri="_SES/SES_PROFILLERI.json yok ya da boş (ses-tasarimcisi·kadro)"))
    zorunlu = e("ses_profil_alanlari", list(ids_profil_alanlari()))
    for k in konusan:
        p = prof.get(k)
        if not isinstance(p, dict):
            if prof: out.append(m("profil_eksik", "HATA", birim=k, olcu="profil yok")); continue
            continue
        if p.get("yol") == "veo_ham" or p.get("rol") == "figuran":
            if p.get("yol") != "veo_ham" or not p.get("kural"):
                out.append(m("figuran_kurali", "HATA", birim=k, oneri="{rol: figuran, yol: veo_ham, kural: '…'}"))
            continue
        eksik = [a for a in zorunlu if p.get(a) in (None, "", [], {})]
        if eksik: out.append(m("profil_eksik", "HATA", birim=k, olcu=eksik))
        out += ids.tarif_denetle(p.get("veo_ses_tarifi"), p, E, birim=k)
        if str(p.get("aksan") or "").lower() in ("neutral", "notr", "nötr", "bilinmiyor"):
            out.append(m("aksan_notr", "BAYRAK", birim=k, olcu=p.get("aksan"), oneri="aksan sözlüğünden somut aksan"))
        ev = (evren_sesleri or {}).get(k)
        if isinstance(ev, dict) and ev.get("durum") == "kilitli" and ev.get("veo_ses_tarifi") and ev["veo_ses_tarifi"] != p.get("veo_ses_tarifi"):
            out.append(m("evren_sesi_degisti", "HATA", birim=k, olcu=p.get("veo_ses_tarifi"), esik=ev["veo_ses_tarifi"],
                         oneri="evrende kayıtlı karakter yeniden profillenmez"))
        if not (kar.get(k) or {}).get("ad_telaffuz"):
            out.append(m("ad_telaffuz_yok", "BAYRAK", birim=k, oneri="HIKAYE.json karakterler.<id>.ad_telaffuz (A10b telaffuz testi)"))
    for k in yar:
        p = prof.get(k)
        if isinstance(p, dict) and (p.get("veo_ses_tarifi") or (p.get("donusum") or {}).get("motor") or p.get("yol") in YOLLAR):
            out.append(m("yaratik_sesi", "HATA", birim=k, oneri="yaratık dönüştürücüye ve Veo konuşmasına girmez; kit (CC0 katmanları)"))
    if e("ses_profil_ayni_bant_ayrisma", True):
        bant = {}
        for k in konusan:
            p = prof.get(k) or {}
            if p.get("yol") == "veo_ham": continue
            bant.setdefault((p.get("cinsiyet"), p.get("yas_bandi")), []).append(k)
        for (c, y), ks in bant.items():
            for i, a in enumerate(ks):
                for b in ks[i + 1:]:
                    pa, pb = prof.get(a) or {}, prof.get(b) or {}
                    if pa.get("perde") == pb.get("perde") and set(pa.get("tini") or []) == set(pb.get("tini") or []):
                        out.append(m("kadro_ayrismiyor", "BAYRAK", birim=a, olcu=[a, b], esik="perde ya da tını farklı"))
    for k in prof:
        if k not in kar and not str(k).startswith("_"): out.append(m("profil_hikayede_yok", "BAYRAK", birim=k))
    return out, konusan


def ids_profil_alanlari():
    return ("cinsiyet", "yas_bandi", "aksan", "perde", "tini", "tempo", "enerji", "veo_ses_tarifi", "ses_etiketi_tr")


def profil_denetle(o):
    film = o["film"]; g = gorev_baglami(o.get("--tur"), "A06s")
    h = hikaye_oku(film)
    if not h:
        rapor_yaz(film, g, "PROFIL", [m("hikaye_yok", "HATA")], "_RAPOR/S0_PROFIL_t{tur}.json"); return BITTI
    prof = ids.profiller_oku(film)
    ev = {k: evren_json(h, "karakterler", k, "ses.json") for k in karakterler(h)}
    olc, konusan = profil_olcumleri(h, prof, evren_sesleri=ev)
    _, r = rapor_yaz(film, g, "PROFIL", olc, "_RAPOR/S0_PROFIL_t{tur}.json", birimler=konusan,
                     ek={"konusan": konusan, "profil_sayisi": len(prof)})
    if prof and not os.path.isfile(os.path.join(film, SES, "SES_KADROSU.md")):
        metin_yaz(os.path.join(film, SES, "SES_KADROSU.md"), kadro_ozeti(h, prof, r))
    return BITTI


# --- A08: taslak ------------------------------------------------------------------------------------------------------
def ic_mi(mekan, grp, evm):
    if isinstance(grp.get("ic"), bool): return grp["ic"]
    if isinstance(evm, dict) and evm.get("ic_dis") in ("ic", "dis"): return evm["ic_dis"] == "ic"
    ad = str(mekan or "").lower()
    return any(re.search(r"(^|_)" + w + r"($|_)", ad) for w in IC_MEKAN)


def _efekt_sozlugu(): return (ortak.json_oku(os.path.join(HERE, "veri", "efekt_sozlugu.json"), {}) or {}).get("fiiller") or {}


def _malzeme(kaynak, a, mekan, zemin, kostum):
    if kaynak == "zemin:mekan": return f"zemin:{zemin or mekan}"
    if kaynak == "kostum": return f"kostum:{a.get('ozne')}/{kostum.get(a.get('ozne'), 'k1')}"
    if kaynak == "nesne": return f"nesne:{a.get('nesne') or a.get('hedef') or 'bilinmiyor'}"
    if kaynak == "oge": return f"oge:{a.get('hedef') or a.get('nesne') or 'bilinmiyor'}"
    return f"ses:{a.get('ozne')}"


def _zemin_en(malzeme):
    z = str(malzeme or "").split(":", 1)[-1]
    return ZEMIN_EN.get(z, "the ground")


def flow_sound_derle(efektler, yatak_ifadesi, tavan=12):
    olaylar = sorted((x for x in efektler if x.get("kategori") in EFEKT_EN),
                     key=lambda x: EFEKT_ONCELIK.index(x["kategori"]) if x["kategori"] in EFEKT_ONCELIK else 99)
    parcalar = []
    for x in olaylar:
        p = EFEKT_EN[x["kategori"]].format(zemin=_zemin_en(x.get("malzeme")))
        if p not in parcalar: parcalar.append(p)
        if len(parcalar) == 2: break
    while True:
        govde = ", ".join(parcalar + [yatak_ifadesi])
        if ids.kelime_sayisi(govde) <= tavan or not parcalar: break
        parcalar.pop()
    return f"Sound: {govde}. No music."


def yatak_ifadesi(zaman, ic, katmanlar):
    hava = (zaman or {}).get("hava")
    if any(re.search(r"ocak|ates|mesale|alev", str(k.get("kaynak", "")) + str(k.get("ad", ""))) for k in katmanlar):
        return "a hearth crackling" if ic else "torches crackling"
    if hava in HAVA_EN: return ("muffled " + HAVA_EN[hava]) if ic else HAVA_EN[hava]
    return "a quiet room" if ic else "a quiet outdoor hush"


def taslak_kur(plan, h, defter, prof, E=None):
    """{S: taslak sözlüğü}."""
    E = E or E_(); sozluk = _efekt_sozlugu(); kurallar = [k for k in (ogrenilen().get("kurallar") or [])
                                                       if k.get("durum") == "aktif" and k.get("tur") == "yol_kurali"]
    hs = hikaye_sahneleri(h); kar = karakterler(h)
    kostum = {k: ((v or {}).get("kostum") or {}).get("varsayilan", "k1") for k, v in kar.items()}
    dl = E.get("diyalog_lufs") if hasattr(E, "get") else None
    normal = (dl or {}).get("normal", -19.5) if isinstance(dl, dict) else -19.5
    ef_db = -orta(e("efekt_diyalog_alti_db"), 6.5)
    yatak_lufs = round(normal - orta(e("ambiyans_diyalog_alti_db"), 15.0), 1)
    capraz = orta(e("ambiyans_capraz_gecis_sn"), 0.75)
    sa = (defter or {}).get("ses_alanlari") or {}
    out, onceki = {}, None
    for S, ps in gruplar(plan).items():
        if S == "_grupsuz": continue
        grp = (plan.get("sahne_gruplari") or {}).get(S) or {}
        mekan = grp.get("mekan"); zaman = grp.get("zaman") or {}
        evm = evren_json(h, "mekanlar", mekan, "ses.json") if mekan else None
        ic = ic_mi(mekan, grp, evm); yer = "ic" if ic else "dis"
        zemin = ((evm or {}).get("zemin_malzemesi") or {}).get(yer) or (zaman.get("hava") == "kar" and not ic and "kar") or None
        notlar = []
        katmanlar = []
        kosul = {k.get("kosul"): k for k in (evm or {}).get("katman_kurallari") or [] if isinstance(k, dict)}
        for x in (sa.get(S) or {}).get("yatak_katmanlari") or []:
            kk = kosul.get(x) or {}
            katmanlar.append({"ad": re.sub(r"[^a-z0-9]+", "_", x.lower()).strip("_"), "dosya": kk.get("katman"),
                              "kazanc_db": kk.get("kazanc_db", -12), "kaynak": f"defter:{x}"})
        hava = zaman.get("hava")
        if hava and hava not in ("acik", "yok", "temiz") and not any(f"hava={hava}" in k["kaynak"] for k in katmanlar):
            katmanlar.append({"ad": f"hava_{hava}", "dosya": None, "kazanc_db": -6 if not ic else -14, "kaynak": f"zaman:hava={hava}"})
        surekli = bool(onceki and onceki["mekan"] == mekan and zaman.get("atlama") == "yok")
        if surekli:
            yatak = json.loads(json.dumps(onceki["yatak"]))
            notlar.append(f"aynı mekân ve kesintisiz zaman: {onceki['S']} yatağı sürer (S0.10)")
        else:
            yatak = {"dosya": ((evm or {}).get("varsayilan_yatak") or {}).get(yer),
                     "etiket": f"{yer.upper()}_{mekan}_{zaman.get('gun_saati') or zaman.get('saat') or 'gun'}_{hava or 'acik'}",
                     "seviye_lufs": yatak_lufs, "dongu": True, "katmanlar": katmanlar}
            if not yatak["dosya"]: notlar.append("yatak dosyası evrende yok; kütüphane eşlemesi (ses_kutuphanesi) A10c'de")
        yatak["katmanlar"] = katmanlar
        ilk_gecis = ((ps[0].get("zanaat") or {}).get("zincir") or {}).get("gecis_turu") if ps else None
        gecis = {"capraz_sn": 0.0 if (surekli or ilk_gecis == "devam") else capraz, "one_alma_sn": None,
                 "zaman_surekli_onceki": surekli}
        oda = ((evm or {}).get("oda") or {}).get("oda_ir") or (f"{yer}_{mekan}" if mekan else None)
        hsahne = hs.get(((grp.get("hikaye") or {}).get("sahne")) or S) or {}
        planlar, eksik = {}, []
        for i, s in enumerate(ps):
            n = s.get("no"); efek = []; harf = iter("abcdefghijklmnopqrstuvwxyz")
            for a in adimlar(s):
                f = sozluk.get(a.get("fiil"))
                if f:
                    efek.append({"id": f"E{n}{next(harf)}", "adim": a.get("id"), "kategori": f["kategori"],
                                 "malzeme": _malzeme(f.get("malzeme"), a, mekan, zemin, kostum), "an": f.get("an", "orta"),
                                 "kaynak_tercih": "klip", "yedek": "kutuphane", "seviye_db_diyaloga_gore": round(ef_db, 1)})
                elif a.get("tur") == "fiziksel":
                    efek.append({"adim": a.get("id"), "sessiz_adim": True, "neden": None,
                                 "taslak_notu": f"'{a.get('fiil')}' efekt sözlüğünde yok: efekt yaz ya da sessizlik gerekçesi"})
                    eksik.append({"plan": n, "adim": a.get("id"), "fiil": a.get("fiil")})
            yol, neden = yol_onerisi(s, h, prof, kurallar)
            ses = {"diyalog": ({"yol": yol, "yol_neden": neden, "seviye_ozel": None} if yol else None), "efektler": efek,
                   "flow_sound": flow_sound_derle(efek, yatak_ifadesi(zaman, ic, katmanlar), e("flow_sound_kelime_max", 12)),
                   "sessizlik": None, "dis_katman_db": None}
            if i == 0: ses["sessizlik"] = sessizlik_onerisi(hsahne.get("vurus"))
            planlar[str(n)] = ses
        out[S] = {"_surum": 1, "sahne_grubu": S, "hikaye_sahne": hsahne.get("id"),
                  "ses": {"yatak": yatak, "oda_yaniti": oda, "gecis": gecis, "kalabalik": None},
                  "planlar": planlar, "eksik_efektler": eksik, "notlar": notlar}
        onceki = {"S": S, "mekan": mekan, "yatak": yatak}
    return out


def sessizlik_onerisi(vurus):
    if vurus == "soguk_acilis":
        return {"tip": "muziksiz", "bas_sn": 0.0, "sure_sn": orta(e("soguk_acilis_muziksiz_sn"), 4.0), "neden": "soguk_acilis"}
    if vurus == "en_karanlik":
        return {"tip": "muziksiz", "bas_sn": 0.0, "sure_sn": float((e("en_karanlik_muziksiz_sn") or [10, 40])[0]) + 5, "neden": "en_karanlik"}
    if vurus in ("ifsa", "sok"):
        return {"tip": "muziksiz", "bas_sn": 0.0, "sure_sn": round(orta(e("vurgu_sessizlik_sn"), 1.9), 1),
                "neden": "ifsa_oncesi" if vurus == "ifsa" else "sok_sonrasi"}
    return None


def taslak(o):
    film = o["film"]
    plan, kod = sahneler_v2(film)
    if plan is None: return kod
    h = hikaye_oku(film); defter = ortak.json_oku(os.path.join(film, "DUNYA_DEFTERI.json"), {}) or {}
    t = taslak_kur(plan, h, defter, ids.profiller_oku(film))
    zarf = {"asama": "A08", "gorev": gorev_baglami(None, "A08")["id"], "arac_surum": SURUM, "zaman": kapi.simdi(), "ortam": kapi.ortam()}
    for S, v in t.items():
        ortak.atomik_yaz(os.path.join(film, SES, f"SES_{S}.taslak.json"), dict(v, _uretim=zarf, _taslak=True))
    eksik = sum(len(v["eksik_efektler"]) for v in t.values())
    print(f"TASLAK: {len(t)} sahne grubu · {sum(len(v['planlar']) for v in t.values())} plan · eşleşmeyen fiziksel adım {eksik} → {SES}/")
    return BITTI


# --- A08: tasarımı uygula ve S0 ---------------------------------------------------------------------------------------
def ses_dosyalari(film):
    out = []
    for p in sorted(glob.glob(os.path.join(film, SES, "SES_*.json"))):
        ad = os.path.basename(p)
        if ad == "SES_PROFILLERI.json" or ad.endswith(".taslak.json"): continue
        j = ortak.json_oku(p)
        out.append((os.path.relpath(p, film), j))
    return out


def uygula(plan, dosyalar):
    """Ses tasarımı dosyalarını SAHNELER görünümüne uygular. (yeni plan, ölçümler, uygulanan gruplar)."""
    p = json.loads(json.dumps(plan)); olc = []; sahip = {}
    nolar = {str(s.get("no")): s for s in p.get("sahneler") or [] if isinstance(s, dict)}
    for rel, j in dosyalar:
        if not isinstance(j, dict): olc.append(m("ses_dosyasi_bozuk", "HATA", olcu=rel)); continue
        S = j.get("sahne_grubu")
        if not S or S not in (p.get("sahne_gruplari") or {}):
            olc.append(m("ses_dosyasi_grup", "HATA", olcu=rel, neden=f"sahne_grubu bilinmiyor: {S!r}")); continue
        if S in sahip: olc.append(m("ses_dosyasi_cift", "HATA", birim=S, olcu=[sahip[S], rel])); continue
        sahip[S] = rel
        for k in j:
            if k not in ("_surum", "_uretim", "_sahip", "sahne_grubu", "hikaye_sahne", "ses", "planlar", "eksik_efektler", "notlar",
                         "_taslak", "gerekce"):
                olc.append(m("ses_alani_disi_yazim", "HATA", birim=S, olcu=k))
        gs = j.get("ses") or {}
        for k in gs:
            if k not in GRUP_SES_ALANLARI: olc.append(m("ses_alani_disi_yazim", "HATA", birim=S, olcu=f"ses.{k}"))
        p["sahne_gruplari"][S]["ses"] = {k: gs.get(k) for k in GRUP_SES_ALANLARI if k in gs}
        for n, v in (j.get("planlar") or {}).items():
            s = nolar.get(str(n))
            if s is None or grup_adi(s) != S: olc.append(m("ses_plan_bilinmiyor", "HATA", birim=S, olcu=n)); continue
            if not isinstance(v, dict): olc.append(m("ses_dosyasi_bozuk", "HATA", plan=s.get("no"))); continue
            for k in v:
                if k not in PLAN_SES_ALANLARI:
                    olc.append(m("ses_alani_disi_yazim" if k != "_derlenir" else "derlenir_ajan_yazimi", "HATA", plan=s.get("no"), olcu=k))
            s.setdefault("zanaat", {})["ses"] = {k: v.get(k) for k in PLAN_SES_ALANLARI}
    return p, olc, sorted(sahip)


def _an_zamani(x, a):
    b, s = float(a.get("bas") or 0), float(a.get("bit") or a.get("bas") or 0)
    an = str(x.get("an") or "orta")
    if an.startswith("ofset:"):
        try: return b + float(an.split(":", 1)[1])
        except ValueError: return None
    return {"bas": b, "orta": (b + s) / 2, "bit": s, "son": s, "yayil": b}.get(an)


def plan_olcumleri(s, h, prof, E, kurallar):
    n = s.get("no"); z = s.get("zanaat") or {}; ses = ses_of(s); out = []
    if not z: return [m("zanaat_yok", "HATA", n)]
    if z.get("plan_tipi") == "kart": return out
    if not z.get("ses"): return [m("ses_tasarimi_yok", "HATA", n, oneri="ses-tasarimcisi·tasarim (zanaat.ses)")]
    dy = ses.get("diyalog") or {}
    # S0.1
    if konusur_mu(s):
        yol = dy.get("yol"); beklenen = beklenen_yol(s, h, prof, kurallar)
        if yol not in YOLLAR: out.append(m("S0.1", "HATA", n, alt="yol_yok", olcu=yol, esik=beklenen))
        elif yol != beklenen and not (dy.get("yol_neden") or "").strip():
            out.append(m("S0.1", "HATA", n, alt="yol_cekisiyor", olcu=yol, esik=beklenen,
                         neden=f"agiz_gorunur={(s.get('_derlenir') or {}).get('agiz_gorunur')}", oneri="yolu düzelt ya da yol_neden yaz"))
        if (s.get("_derlenir") or {}).get("agiz_gorunur") not in ("tam", "kismi", "yok"):
            out.append(m("S0.1", "HATA", n, alt="agiz_gorunur_yok", oneri="_derlenir.agiz_gorunur (kroki/plan_birlestir)"))
        if yol == "veo_ham" and (s.get("replik") or {}).get("karakter") not in figuranlar(h, prof):
            out.append(m("S0.1", "HATA", n, alt="veo_ham_figuran_degil", olcu=(s.get("replik") or {}).get("karakter")))
    elif dy.get("yol"):
        out.append(m("S0.1", "HATA", n, alt="konusmasiz_planda_yol", olcu=dy.get("yol")))
    # S0.2
    if not dinleyen_agiz_kurali(s): out.append(m("S0.2", "HATA", n, olcu=(s.get("_derlenir") or {}).get("dinleyen_agiz"), esik="kapali"))
    # S0.6
    out += ids.flow_sound_denetle(ses.get("flow_sound"), E, n)
    # S0.7–S0.9 + yedek
    ad = {a.get("id"): a for a in adimlar(s)}
    efek = [x for x in ses.get("efektler") or [] if isinstance(x, dict)]
    pay = e("efekt_an_pay_sn", 0.3); uzak = e("efekt_soz_uzaklik_min_ms", 150) / 1000.0
    ani = set(e("efekt_ani_kategoriler", []) or [])
    sozler = [b for _, b, _ in replik_pencereleri(s)]; soz0 = min(sozler) if sozler else None
    for a in ad.values():
        if a.get("tur") != "fiziksel": continue
        kap = [x for x in efek if x.get("adim") == a.get("id")]
        if not any((not x.get("sessiz_adim")) or (x.get("neden") or "").strip() for x in kap):
            out.append(m("S0.7", "HATA", n, olcu=a.get("id"), alt="efektsiz_fiziksel_adim", oneri="efekt olayı ya da gerekçeli sessiz_adim"))
    for x in efek:
        if x.get("sessiz_adim"): continue
        a = ad.get(x.get("adim"))
        if a is None: out.append(m("S0.8", "HATA", n, alt="adim_yok", olcu=x.get("adim"))); continue
        t = _an_zamani(x, a)
        if t is None or not (float(a.get("bas") or 0) - 1e-6 <= t <= float(a.get("bit") or 0) + pay + 1e-6):
            out.append(m("S0.8", "BAYRAK", n, olcu={"efekt": x.get("id"), "an": x.get("an"), "t": t}, esik=f"[bas, bit + {pay}]"))
        if t is not None and soz0 is not None and x.get("kategori") in ani and not x.get("bilincli_sok") and abs(t - soz0) < uzak:
            out.append(m("S0.9", "BAYRAK", n, olcu={"efekt": x.get("id"), "fark_ms": round(abs(t - soz0) * 1000)}, esik=f"≥ {int(uzak * 1000)} ms"))
        if not x.get("yedek"): out.append(m("efekt_yedek_yok", "HATA", n, olcu=x.get("id"), oneri="klip seçilse de yedek zorunlu"))
    # S0.21
    rep = s.get("replik") or {}
    if rep.get("metin"):
        t = rep.get("teslim")
        if not isinstance(t, str) or t not in ids.teslim_sozlugu():
            out.append(m("S0.21", "BAYRAK", n, alt="teslim", olcu=t, esik="tek teslim, sözlükte"))
        elif t == "fisilti" and (s.get("_derlenir") or {}).get("agiz_gorunur") == "tam" and dy.get("yol") == "veo_donustur":
            if any(k.get("durum") == "aktif" and k.get("kategori") in ("donusum_metalik", "fisilti") for k in ogrenilen().get("kurallar") or []):
                out.append(m("S0.21", "BAYRAK", n, alt="fisilti_donusum_dersi", oneri="dönüştürücü fısıltıda zorlanır (ders kuralı)"))
    return out


def grup_olcumleri(plan, defter, ids_=None):
    out = []; sa = (defter or {}).get("ses_alanlari") or {}; onceki = None
    for S, ps in gruplar(plan).items():
        if S == "_grupsuz": continue
        grp = (plan.get("sahne_gruplari") or {}).get(S) or {}; gs = grp.get("ses") or {}; zaman = grp.get("zaman") or {}
        if ids_ is not None and S not in ids_: onceki = (S, grp); continue
        y = gs.get("yatak")
        if isinstance(y, list) and len(y) > e("yatak_sahne_grubu_max", 1) or any(k in gs for k in ("yatak2", "yataklar")):
            out.append(m("S0.10", "HATA", birim=S, alt="birden_cok_yatak"))
        elif not isinstance(y, dict) or not (y.get("dosya") or y.get("etiket")):
            out.append(m("S0.10", "HATA", birim=S, alt="yatak_yok"))
        if onceki and isinstance(y, dict):
            pS, pg = onceki; py = ((pg.get("ses") or {}).get("yatak")) or {}
            if pg.get("mekan") == grp.get("mekan") and zaman.get("atlama") == "yok":
                if (py.get("dosya"), py.get("etiket")) != (y.get("dosya"), y.get("etiket")):
                    out.append(m("S0.10", "HATA", birim=S, alt="kesintisiz_zamanda_yatak_degisti", olcu=[pS, S]))
            ilk = ((ps[0].get("zanaat") or {}).get("zincir") or {}).get("gecis_turu") if ps else None
            if ilk == "devam" and float(((gs.get("gecis") or {}).get("capraz_sn")) or 0) > 0:
                out.append(m("S0.10", "HATA", birim=S, alt="devamda_capraz_gecis"))
        # S0.11
        if isinstance(y, dict):
            defter_k = set((sa.get(S) or {}).get("yatak_katmanlari") or [])
            var = set()
            for k in y.get("katmanlar") or []:
                kay = str((k or {}).get("kaynak") or "")
                if kay.startswith("defter:"):
                    x = kay[7:]; var.add(x)
                    if x not in defter_k and not _zaman_olgusu(x, zaman):
                        out.append(m("S0.11", "HATA", birim=S, alt="katman_defterde_yok", olcu=x))
                    elif x not in defter_k and not _zaman_tutarli(x, zaman):
                        out.append(m("S0.11", "HATA", birim=S, alt="katman_zamanla_celisiyor", olcu=x, esik=zaman))
                elif kay.startswith("zaman:"):
                    x = kay[6:]; var.add(x)
                    if not _zaman_tutarli(x, zaman): out.append(m("S0.11", "HATA", birim=S, alt="katman_zamanla_celisiyor", olcu=x, esik=zaman))
                else:
                    out.append(m("S0.11", "HATA", birim=S, alt="katman_kaynaksiz", olcu=(k or {}).get("ad")))
            for x in defter_k - var:
                out.append(m("S0.11", "BAYRAK", birim=S, alt="defter_katmani_yatakta_yok", olcu=x))
        onceki = (S, grp)
    return out


def _zaman_olgusu(x, zaman): return bool(re.match(r"^(hava|gun_saati|saat)=", x))


def _zaman_tutarli(x, zaman):
    r = re.match(r"^(hava|gun_saati|saat)=(.+)$", x)
    if not r: return True
    k = r.group(1); v = r.group(2)
    gercek = zaman.get(k) if k != "gun_saati" else (zaman.get("gun_saati") or zaman.get("saat"))
    if k == "saat": gercek = zaman.get("saat") or zaman.get("gun_saati")
    return gercek == v


def film_olcumleri(plan, h, E):
    out = []; ps = plan_listesi(plan)
    # S0.3
    for x in ses_tanitim_kurali(ps): out.append(m("S0.3", "BAYRAK", x["plan"], olcu=x["karakter"], esik="önce ekranda konuşurken duyulmalı"))
    # S0.12
    mut = [(s, ses_of(s).get("sessizlik")) for s in ps if (ses_of(s).get("sessizlik") or {}).get("tip") == "mutlak"]
    if len(mut) > e("mutlak_sessizlik_film_max", 2): out.append(m("S0.12", "HATA", olcu=len(mut), esik=e("mutlak_sessizlik_film_max", 2)))
    for s, x in mut:
        if float(x.get("sure_sn") or 0) > e("mutlak_sessizlik_max_sn", 1.0):
            out.append(m("S0.12", "HATA", s.get("no"), olcu=x.get("sure_sn"), esik=e("mutlak_sessizlik_max_sn", 1.0)))
    # S0.13
    hs = hikaye_sahneleri(h)
    for S, gps in gruplar(plan).items():
        grp = (plan.get("sahne_gruplari") or {}).get(S) or {}
        v = (hs.get(((grp.get("hikaye") or {}).get("sahne")) or S) or {}).get("vurus")
        if not gps or v not in ("soguk_acilis", "en_karanlik", "ifsa", "sok"): continue
        ss = [ses_of(s).get("sessizlik") for s in gps if ses_of(s).get("sessizlik")]
        ar = {"soguk_acilis": e("soguk_acilis_muziksiz_sn", [3, 5]), "en_karanlik": e("en_karanlik_muziksiz_sn", [10, 40])}.get(
            v, e("vurgu_sessizlik_sn", [0.8, 3.0]))
        if v == "soguk_acilis":
            iyi = [x for x in ss if x.get("tip") == "muziksiz" and float(x.get("bas_sn") or 0) == 0 and float(x.get("sure_sn") or 0) >= ar[0]]
        else:
            iyi = [x for x in ss if x.get("tip") == "muziksiz" and ar[0] <= float(x.get("sure_sn") or 0) <= ar[1]]
        if not iyi: out.append(m("S0.13", "BAYRAK", birim=S, alt=v, esik=ar, oneri="planlı müziksiz an"))
    return out


def ertelenen_maddeler(film, plan, h, prof):
    """S0.19 / S0.20: A10b/A10c raporları varsa ölç, yoksa ertele. (ölçümler, ertelenen)"""
    out, ert = [], []
    konusan = {(s.get("replik") or {}).get("karakter") for s in plan_listesi(plan) if (s.get("replik") or {}).get("metin")}
    konusan.discard(None)
    if os.path.isfile(os.path.join(film, "_RAPOR", "S1_FILM.json")):
        for k in sorted(konusan):
            if k in figuranlar(h, prof): continue
            if not evren_json(h, "karakterler", k, "ses.json"): out.append(m("S0.19", "HATA", birim=f"ses:{k}", olcu=k))
    else: ert.append("S0.19 (A10c ses seçiminden sonra)")
    tel = ortak.json_oku(os.path.join(film, "_RAPOR", "S1a_telaffuz.json"))
    if isinstance(tel, dict):
        if tel.get("sonuc") not in ("GEC", "BAYRAK"): out.append(m("S0.20", "HATA", olcu=tel.get("sonuc"), kanit="_RAPOR/S1a_telaffuz.json"))
    else: ert.append("S0.20 (A10b telaffuz testinden sonra)")
    return out, ert


def derlenir_doldur(p, muzik_ipuclari=None):
    ts = ids.teslim_sozlugu()
    for s in p.get("sahneler") or []:
        rep = s.get("replik") or {}; d = s.setdefault("_derlenir", {})
        t = ts.get(rep.get("teslim")) if isinstance(rep.get("teslim"), str) else None
        if rep.get("metin") and t:
            d.setdefault("ton_fiili_en", t.get("en")); d.setdefault("seviye", t.get("lufs"))
        if muzik_ipuclari is not None: d["muzik_ipucu"] = muzik_ipuclari.get(s.get("no"))
    return p


def yeniden_yaz(film, olc, plan):
    try: import kuyruk
    except Exception: return None
    grp_sahne = {S: (((plan.get("sahne_gruplari") or {}).get(S) or {}).get("hikaye") or {}).get("sahne") or S
                 for S in plan.get("sahne_gruplari") or {}}
    plan_grup = {s.get("no"): grup_adi(s) for s in plan_listesi(plan)}
    maddeler = []
    for x in olc:
        kn = KOK_NEDEN.get(x["madde"])
        if x["seviye"] != "HATA" or not kn: continue
        konum = {}
        if isinstance(x.get("plan"), int): konum["plan"] = x["plan"]; S = plan_grup.get(x["plan"])
        else: S = x.get("birim")
        if S in grp_sahne and re.fullmatch(r"S[0-9]{2,}", str(grp_sahne[S])): konum["sahne"] = grp_sahne[S]
        if not konum: continue
        maddeler.append({"konum": konum, "kapi": "S0", "madde": x["madde"], "kok_neden": kn, "yazar": "ses-tasarimcisi",
                         "oneri": x.get("oneri") or x.get("alt") or x["madde"]})
    if not maddeler: return None
    try: return kuyruk.yaz_ekle(film, maddeler, "A08")
    except Exception as ex:
        print(f"!! YENIDEN_YAZ yazılamadı ({ex.__class__.__name__}); maddeler raporda"); return None


def denetle(o):
    film = o["film"]; S_tek = o.get("--sahne")
    g = gorev_baglami(o.get("--tur"), "A08")
    plan, kod = sahneler_v2(film)
    kapsam = S_tek or "FILM"; varsayilan = f"_RAPOR/S0_{kapsam}.json"
    if plan is None:
        rapor_yaz(film, g, kapsam, [m("sahneler_yok", "HATA")], varsayilan); return kod if kod == ORTAM else BITTI
    h = hikaye_oku(film); defter = ortak.json_oku(os.path.join(film, "DUNYA_DEFTERI.json"), {}) or {}
    prof = ids.profiller_oku(film); E = E_()
    kurallar = [k for k in (ogrenilen().get("kurallar") or []) if k.get("durum") == "aktif" and k.get("tur") == "yol_kurali"]
    dosyalar = ses_dosyalari(film)
    if S_tek: dosyalar = [(r, j) for r, j in dosyalar if isinstance(j, dict) and j.get("sahne_grubu") == S_tek]
    p, olc, uygulanan = uygula(plan, dosyalar)
    grs = gruplar(p)
    hedef = [S_tek] if S_tek else [S for S in grs if S != "_grupsuz"]
    if S_tek and S_tek not in grs: olc.append(m("sahne_grubu_yok", "HATA", birim=S_tek))
    for S in hedef:
        if S not in uygulanan and not ((p.get("sahne_gruplari") or {}).get(S) or {}).get("ses"):
            olc.append(m("sahne_grubu_ses_yok", "HATA", birim=S, oneri=f"_SES/SES_<i>.json (sahne_grubu: {S})"))
    birimler = []
    for S in hedef:
        for s in grs.get(S, []):
            birimler.append(s.get("no")); olc += plan_olcumleri(s, h, prof, E, kurallar)
    if "_grupsuz" in grs and not S_tek:
        for s in grs["_grupsuz"]: olc.append(m("plan_grupsuz", "HATA", s.get("no")))
    olc += grup_olcumleri(p, defter, set(hedef))
    for S in hedef: birimler.append(S)
    ek = {"ses_dosyalari": [r for r, _ in dosyalar], "uygulanan_gruplar": uygulanan}
    ipuclari = None
    if not S_tek:
        olc += film_olcumleri(p, h, E)
        import muzik
        liste = muzik.liste_oku(film)
        mo, ipuclari = muzik.kagit_olcumleri(p, liste, h, E, muzik.motifler(film, h, liste))
        olc += mo
        e2, ert = ertelenen_maddeler(film, p, h, prof); olc += e2; ek["ertelenen"] = ert
        if any(s.get("hareket_istem") for s in plan_listesi(p)):
            olc += ids.denetle(p, profiller=prof, E=E, yaratiklar=yaratiklar(h))
    hata = any(x["seviye"] == "HATA" for x in olc)
    ek["sahneler_yazildi"] = bool(not S_tek and not hata)
    _, r = rapor_yaz(film, g, kapsam, olc, varsayilan, birimler=birimler, ek=ek)
    if ek["sahneler_yazildi"]:
        doc = derlenir_doldur(p, ipuclari)
        ortak.atomik_yaz(os.path.join(film, "SAHNELER.json"), doc)
        imza_tazele(film, doc)
        metin_yaz(os.path.join(film, SES, "SES_TASARIMI.md"), tasarim_ozeti(doc, r))
    elif hata and not S_tek:
        yeniden_yaz(film, r["hatalar"], plan)
    return BITTI


def imza_tazele(film, doc):
    """_derlenir'e kod yazdı: plan_sema'nın elle yazım denetimi için imzalar tazelenir (istem_derle ile aynı yol)."""
    if not os.path.isdir(os.path.join(film, "_YONETMEN")): return
    try:
        import plan_birlestir
        plan_birlestir.imza_yaz(film, doc)
    except Exception as ex:
        print(f"!! _derlenir imzası tazelenemedi ({ex.__class__.__name__}); plan_birlestir yeniden koşunca düzelir")


def metin_yaz(yol, metin):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol + ".tmp", "w", encoding="utf-8") as f: f.write(metin)
    os.replace(yol + ".tmp", yol)


def tasarim_ozeti(doc, r):
    """_SES/SES_TASARIMI.md: insan için özet (bilgi; kaynak SAHNELER.json + S0 raporu)."""
    yol = {}; satir = ["# Ses tasarımı (özet)", "", f"S0: {r['sonuc']} · HATA {len(r['hatalar'])} · BAYRAK {len(r['bayraklar'])}", ""]
    for s in plan_listesi(doc):
        y = (ses_of(s).get("diyalog") or {}).get("yol")
        if y: yol[y] = yol.get(y, 0) + 1
    satir.append("Diyalog yolları: " + (", ".join(f"{k} {v}" for k, v in sorted(yol.items())) or "yok"))
    satir.append("")
    for S, ps in gruplar(doc).items():
        if S == "_grupsuz": continue
        gs = ((doc.get("sahne_gruplari") or {}).get(S) or {}).get("ses") or {}; y = gs.get("yatak") or {}
        ef = sum(len([x for x in ses_of(s).get("efektler") or [] if not x.get("sessiz_adim")]) for s in ps)
        ss = [s.get("no") for s in ps if ses_of(s).get("sessizlik")]
        satir.append(f"- {S}: yatak {y.get('etiket') or y.get('dosya')} ({len(y.get('katmanlar') or [])} katman) · efekt {ef}"
                     + (f" · sessizlik: plan {ss}" if ss else ""))
    return "\n".join(satir) + "\n"


def kadro_ozeti(h, prof, r):
    satir = ["# Ses kadrosu (özet)", "", f"Profil denetimi: {r['sonuc']} · HATA {len(r['hatalar'])} · BAYRAK {len(r['bayraklar'])}", ""]
    for k, p in sorted(prof.items()):
        satir.append(f"- {(karakterler(h).get(k) or {}).get('ad') or k}: {p.get('veo_ses_tarifi') or p.get('yol') or p.get('tur') or '—'}"
                     + (f" · {p.get('ses_etiketi_tr')}" if p.get("ses_etiketi_tr") else ""))
    return "\n".join(satir) + "\n"


KOMUTLAR = {"--profil-denetle": profil_denetle, "--taslak": taslak, "--denetle": denetle}


def main(a):
    kom = [k for k in KOMUTLAR if k in a]
    if len(kom) != 1: print(__doc__); return ORTAM
    o = {}
    for k in ("--film", "--tur", "--sahne"):
        if k in a and a.index(k) + 1 < len(a): o[k] = a[a.index(k) + 1]
    if not o.get("--film"): print("!! --film gerekli"); return ORTAM
    try:
        f = o["--film"]
        o["film"] = os.path.abspath(f) if os.path.isdir(f) else os.path.join(ortak.yollar()["filmler"], f)
        if not os.path.isdir(o["film"]): print(f"!! film klasörü yok: {o['film']}"); return HATA
        return KOMUTLAR[kom[0]](o)
    except ortak.YolYok as ex:
        print("!!", ex); return ORTAM
    except kapi.RaporHatasi as ex:
        print("!! rapor yazılamadı:", ex); return HATA


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
