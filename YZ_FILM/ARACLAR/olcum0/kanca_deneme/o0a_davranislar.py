"""DAVRANISLAR — TASARIM §10.3'teki 20 Claude Code davranışının kataloğu ve değerlendiricileri (Ö0-a; o0a_kos.py kullanır).

Her madde: no, baslik, adimlar (geliştirici Claude'a yönerge; {I} işaret komutu öneki, {K} --kayit, {YAZMA}, {PAKET}, {PY}, {SONDA}),
kip (SONDA_KIP.json'a yazılacak engelleme kipi), hazirlik (o0a_kos.py'nin adım öncesi işi), yedek (çalışmazsa seçilen yedek; TASARIM'daki),
degerlendir(olaylar, bag) → {"sonuc": "calisiyor" | "calismiyor" | None (karar için elle bilgi gerekir), "olcu": {...}, "not": str}.
olaylar: sonda kayıtları (yalnız bu adımın başlangıcından sonrası); bag: {"elle": {alan: değer}, "otomatik": {...}, "tum": bütün kayıtlar,
"sonuclar": önceki sonuçlar}. Değerlendiriciler saf işlevdir (dosya okumaz); testler sahte kayıtlarla sınar.
"""

CALISIYOR, CALISMIYOR = "calisiyor", "calismiyor"
ANA_OLAYLAR = ("komut", "ajan", "erisim", "arac_sonrasi", "stop", "istem")


# --- yardımcılar -------------------------------------------------------------------------------------------------------
def ana(o): return not o.get("agent_id")


def isaretler(ol, ad=None, onek=None, asama=None):
    return [o for o in ol if o.get("olay") == "isaret" and (ad is None or o.get("ad") == ad) and (onek is None or str(o.get("ad", "")).startswith(onek))
            and (asama is None or o.get("asama") == asama)]


def olaylar_(ol, olay, **k):
    return [o for o in ol if o.get("olay") == olay and all(o.get(a) == v for a, v in k.items())]


def evet(v):
    return str(v).strip().lower() in ("1", "true", "evet", "e", "yes", "var", "calisiyor", "listede")


def kullanici_istemi_mi(o):
    """Gerçek kullanıcı istemi mi? Masaüstü uygulamasında arka plan işinin bildirimi oturuma UserPromptSubmit olarak (ör. <task-notification>)
    gelir: sonda onu istem_turu "sistem" diye işaretler (o0a_sonda.istem_turu). İşaretsiz eski kayıt ihtiyatla kullanıcı sayılır."""
    return o.get("olay") == "istem" and o.get("istem_turu") != "sistem"


def uyandi_mi(ol, t_bit):
    """Ana tur (Stop) iş bitmeden kapandıysa: iş bittikten sonraki ilk ana-oturum olayı GERÇEK kullanıcı istemi DEĞİLSE oturum kendiliğinden
    uyandı (bildirimin kendisi istem olarak gelse de). Bildirim kancası (Notification, olay "bildirim") ana olay değildir: sayılmaz.
    Dönüş: True/False; ana tur iş bitmeden kapanmadıysa None (deneme geçersiz: tur bitirilmeden beklendi)."""
    if not [o for o in ol if o.get("olay") == "stop" and ana(o) and o.get("t", 0) < t_bit]: return None
    sonra = sorted([o for o in ol if o.get("t", 0) > t_bit and ana(o) and o.get("olay") in ANA_OLAYLAR], key=lambda o: o["t"])
    if not sonra: return False
    return not kullanici_istemi_mi(sonra[0])


def sonuc(ok, olcu, not_=""):
    return {"sonuc": None if ok is None else (CALISIYOR if ok else CALISMIYOR), "olcu": olcu, "not": not_}


# --- değerlendiriciler -------------------------------------------------------------------------------------------------
def d1(ol, bag):
    p = isaretler(ol, onek="paralel-")
    bas = {o["ad"]: o["t"] for o in p if o.get("asama") == "bas"}; bit = {o["ad"]: o["t"] for o in p if o.get("asama") == "bit"}
    adlar = sorted(set(bas) & set(bit))
    if len(adlar) < 3: return sonuc(None, {"tamamlanan": len(adlar)}, "en az 3 paralel-* işareti gerekli (adım yönergesi)")
    ust = max(sum(1 for b in adlar if bas[b] <= bas[a] < bit[b]) for a in adlar)
    post = sorted(o["t"] for o in ol if o.get("olay") == "arac_sonrasi" and o.get("tool_name") in ("Agent", "Task") and ana(o))
    bekledi = bool(post) and len(post) >= 3 and min(post) >= min(bit.values()) - 0.5
    fork = [o.get("env", {}).get("CLAUDE_CODE_FORK_SUBAGENT") for o in ol if o.get("env")]
    olcu = {"ajan": len(adlar), "en_cok_eszamanli": ust, "ana_bekledi": bekledi, "fork_env": fork[-1] if fork else None}
    return sonuc(ust >= 2 and bekledi, olcu)


def _arka_plan(ad):
    def d(ol, bag):
        b = isaretler(ol, ad=ad, asama="bit")
        if not b: return sonuc(None, {}, f"{ad} işareti bitmedi; bekle ya da adımı yinele")
        u = uyandi_mi(ol, b[-1]["t"])
        if u is None: return sonuc(None, {"bekle_sn": b[-1].get("bekle_sn")}, "ana tur iş bitmeden kapanmadı: turu bitir ve kendiliğinden uyanmayı bekle")
        return sonuc(u, {"uyandi": u, "bekle_sn": b[-1].get("bekle_sn")})
    return d


def d3(ol, bag):
    eng = [o for o in ol if o.get("olay") == "ajan_bitti" and o.get("engelledi")]
    on = bool(isaretler(ol, ad="asama-2-on", asama="bit")); arka = bool(isaretler(ol, ad="asama-2-arka", asama="bit"))
    turlar = isaretler(ol, onek="tur-", asama="bit")
    bitti = [o for o in ol if o.get("olay") == "ajan_bitti" and o.get("agent_type") == "o0a-sonda" and not o.get("engelledi")]
    mt = None; sm = None
    if turlar:
        t_ilk = None
        for o in bitti:
            once = [x for x in turlar if x["t"] < o["t"]]
            if 0 < len(once) < 10: t_ilk = o["t"]; break
        mt = t_ilk is not None
        sm = bool(t_ilk and [x for x in turlar if x["t"] > t_ilk])
    olcu = {"engelleme": len(eng), "on_plan_devam": on, "arka_plan_devam": arka, "maxturns_subagentstop": mt, "sendmessage_devam": sm}
    if not eng: return sonuc(None, olcu, "SubagentStop engellemesi görülmedi (adım 3 kipi açık mı, ajan o0a-sonda mı?)")
    return sonuc(on, olcu, "" if arka else "arka plan devamı görülmedi (olcu)")


def d4(ol, bag):
    a = [o for o in ol if o.get("olay") == "ajan" and o.get("tool_name") in ("Agent", "Task")]
    if not a: return sonuc(None, {}, "PreToolUse Agent kaydı yok")
    t = a[-1]; e = bag.get("elle") or {}
    olcu = {"subagent_type": t.get("subagent_type"), "name_gorunur": t.get("name_var"), "isolation_gorunur": t.get("isolation_var"),
            "anahtarlar": t.get("ti_anahtarlar"), "fork": "ölçülmedi: fork kapalı tutulur (D-10; CLAUDE_CODE_FORK_SUBAGENT=0)",
            "isolation_worktree": e.get("isolation") or None}
    # Ö0-a bulgusu (ilk yerel oturum): Agent aracının şemasında `name` alanı YOK; `isolation: worktree` origin/main ref'i olmadığı için
    # başarısız. Sistem ikisine de dayanmaz: kanca name/isolation verilen çağrıyı zaten reddeder (yalnız subagent_type + istem), görev
    # bağlama istemdeki GOREV.json yolundandır. Karar yalnız subagent_type'ın görünmesine bağlıdır; name/isolation bilgi olarak kalır.
    olcu["not_name_isolation"] = "bilgi: sistem name/isolation kullanmaz (kanca reddeder); karara girmez"
    return sonuc(bool(t.get("subagent_type")), olcu)


def d5(ol, bag):
    b = [o for o in ol if o.get("olay") == "yavas_basladi" and o.get("giris") == "A"]
    if not b: return sonuc(None, {}, "A girişi yavaş kancası başlamadı (komutta O0A_YAVAS_A var mı?)")
    bitti = bool([o for o in ol if o.get("olay") == "yavas_bitti" and o.get("giris") == "A"])
    gecti = bool(isaretler(ol, ad="yavas-a"))
    olcu = {"zaman_asimi_kesti": not bitti, "onfailure_engelledi": not gecti}
    return sonuc((not bitti) and (not gecti), olcu)


def d6(ol, bag):
    e = [o.get("env") or {} for o in ol if o.get("env") and o.get("olay") != "isaret"] or \
        [o.get("env") or {} for o in bag.get("tum", []) if o.get("env") and o.get("olay") != "isaret"]
    if not e: return sonuc(None, {}, "kanca kaydı yok")
    yerel = any(x.get("O0A_SONDA_ENV") == "1" for x in e); fork = any(x.get("CLAUDE_CODE_FORK_SUBAGENT") == "0" for x in e)
    return sonuc(yerel and fork, {"settings_local_env_kancada": yerel, "settings_env_fork_kancada": fork})


def d7(ol, bag):
    yaz = [o for o in ol if o.get("olay") == "erisim" and o.get("tool_name") in ("Write", "Edit") and o.get("agent_id")
           and o.get("dosya_adi") == "ajan_yazdi.txt"]
    dosya = bool((bag.get("otomatik") or {}).get("7", {}).get("dosya_var"))
    izin = [o for o in ol if o.get("olay") == "izin_istegi" or (o.get("olay") == "bildirim" and o.get("izin_mesaji"))]
    elle = (bag.get("elle") or {}).get("soru_soruldu")
    soru = evet(elle) if elle is not None else bool(izin)
    olcu = {"alt_ajan_yazdi": bool(yaz), "dosya_var": dosya, "izin_sorusu": soru, "izin_olayi": len(izin)}
    if not yaz and not dosya: return sonuc(None, olcu, "alt ajan yazımı görülmedi")
    return sonuc(dosya and not soru, olcu)


def d8(ol, bag):
    oto = (bag.get("otomatik") or {}).get("8") or {}
    bash = [o for o in ol if o.get("giris") == "bash" and o.get("olay") == "komut"]
    mutlak = [o for o in ol if o.get("giris") in ("A", "C", "mutlak")]
    ps = [o for o in ol if o.get("tool_name") == "PowerShell"]
    sarmal = [o["sarmal_sure_ms"] for o in bash if o.get("sarmal_sure_ms") is not None]
    olcu = {"bash_sarmal": bool(bash), "mutlak_python": bool(mutlak), "powershell_eslesti": bool(ps) if ps else (bag.get("elle") or {}).get("powershell"),
            "sonda_sarmal_ms_medyan": sorted(sarmal)[len(sarmal) // 2] if sarmal else None,
            "kanca_sh_medyan_sn": oto.get("kanca_sh_medyan_sn"), "kanca_py_medyan_sn": oto.get("kanca_py_medyan_sn"), "windows": oto.get("windows")}
    if not (bash or mutlak) or oto.get("kanca_sh_medyan_sn") is None:
        return sonuc(None, olcu, "canlı Bash kaydı ve `o0a_kos.py otomatik` süre ölçümü gerekli")
    sure_ok = float(oto["kanca_sh_medyan_sn"]) <= 2.0
    return sonuc(bool(bash) and bool(mutlak) and sure_ok, olcu, "" if oto.get("windows") else "Windows dışında ölçüldü: Windows'ta yinelenmeli")


def d9(ol, bag):
    c = [o for o in ol if o.get("olay") == "komut" and o.get("giris") == "C" and "O0A_CIFT" in (o.get("isaretler") or [])]
    d = [o for o in ol if o.get("olay") == "komut" and o.get("giris") == "D" and "O0A_CIFT" in (o.get("isaretler") or [])]
    if not c and not d: return sonuc(None, {}, "O0A_CIFT komutu görülmedi (/o0a-sonda becerisiyle çalıştırılmalı)")
    say = {}
    for o in c: say[o.get("tool_use_id") or "?"] = say.get(o.get("tool_use_id") or "?", 0) + 1
    en = max(say.values()) if say else 0
    olcu = {"beceri_kancasi_kostu": bool(d), "ayni_komut_kosu_sayisi": en, "cift_kosu": en >= 2}
    return sonuc(bool(d), olcu, "aynı komut iki kez koştu: beceri kancası farklı bağımsız değişkenle (--kaynak beceri) kalır" if en >= 2 else "")


def d10(ol, bag):
    p = bool(isaretler(ol, ad="unlem-python")); y = bool(isaretler(ol, ad="unlem-py"))
    if not (p or y) and not isaretler(ol, ad="cift-test"): return sonuc(None, {}, "/o0a-sonda becerisi açılmadı")
    return sonuc(p, {"python_buldu": p, "py310_buldu": y}, "" if p else ("py -3.10 çalışıyor" if y else "ikisi de çalışmadı"))


def d11(ol, bag):
    tum = bag.get("tum") or ol
    s = [o for o in ol if o.get("olay") == "oturum_basi"]
    if not s: return sonuc(None, {}, "yeniden açılış (SessionStart) görülmedi")
    o = s[-1]; onceki = {x.get("session_id") for x in tum if x.get("t", 0) < o.get("t", 0) and x.get("session_id")}
    ist = [x for x in ol if x.get("olay") == "istem" and x.get("t", 0) >= o.get("t", 0)]
    devam = bool(ist and ist[0].get("prompt_devam") and ist[0]["t"] - o["t"] <= 120)
    surdu = o.get("kaynak") == "resume" or (o.get("session_id") in onceki)
    # Ö0-a bulgusu: masaüstü uygulamasında sürdürme aynı konuşmayı açar ama ilk mesaj "devam" olmaz. Sistem ilk mesaja dayanmaz
    # (kanca.py: resume'da OTURUM_SURDURULDU işareti; soru/dur olmayan ilk mesaj "devam" sayılır). Karar yalnız aynı oturumun sürmesi;
    # ilk mesaj bilgi olarak kalır. DEVAM.bat (claude --continue) yedek yol olarak durur.
    return sonuc(surdu, {"kaynak": o.get("kaynak"), "ayni_oturum": o.get("session_id") in onceki, "ilk_mesaj_devam": devam})


def bos_mu(v):
    """Değeri olmayan alan: None, boş/boşluk dizi, boş liste/sözlük (Ö0-a #12: effort anahtarı değersiz geldi)."""
    return v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, (list, dict, tuple)) and not v)


def effort_olcu(tum, elle):
    """effort tanınıyor mu: elle değer (boş değilse) → kanca girdisinde değerli effort → anahtar var ama değer yok ("degersiz") → None.
    "degersiz" ölçülemedi demektir: madde onunla çalışmıyor sayılmaz, olcu'da görünür (yedek: ajan dosyasındaki effort: high kalır,
    kullanım kaydı film.py'nin varsayılanı "high"tır)."""
    if not bos_mu(elle): return elle
    kayit = [o for o in tum if o.get("effort_anahtari")]
    if any(not bos_mu(o.get("effort")) for o in kayit): return True
    return "degersiz" if kayit else None


def d12(ol, bag):
    tum = bag.get("tum") or ol; e = {k: v for k, v in (bag.get("elle") or {}).items() if not bos_mu(v)}; s = bag.get("sonuclar") or {}
    bas = [o for o in tum if o.get("olay") == "ajan_basi" and o.get("agent_type") == "o0a-sonda"]
    bit = [o for o in tum if o.get("olay") == "ajan_bitti" and o.get("agent_type") == "o0a-sonda" and o.get("dokum_var")]
    olcu = {"ajan_yuklendi_bilinmeyen_alanla": bool(bas) or bool(bit),
            "omitClaudeMd": (not any(o.get("claude_md_gorundu") for o in bit)) if bit else None,
            "maxTurns": ((s.get("3") or {}).get("olcu") or {}).get("maxturns_subagentstop"),
            "permissionMode": (((s.get("7") or {}).get("olcu") or {}).get("izin_sorusu") is False) if s.get("7") else None,
            "effort": effort_olcu(tum, e.get("effort")), "beceri_hooks": ((s.get("9") or {}).get("olcu") or {}).get("beceri_kancasi_kostu"),
            "disable-model-invocation": e.get("disable_model_invocation"), "allowed-tools": e.get("allowed_tools"),
            "disallowed-tools": e.get("disallowed_tools")}
    bilinen = {k: v for k, v in olcu.items() if v is not None}
    eksik = [k for k, v in olcu.items() if v is None]
    if eksik: return sonuc(None, olcu, "eksik: " + ", ".join(eksik) + " (3, 7, 9 adımları ve kaydet --alan ile)")
    olculemedi = [k for k, v in bilinen.items() if v == "degersiz"]
    taninmayan_ = [k for k, v in bilinen.items() if k not in olculemedi and not (v is True or evet(v))]
    olcu["taninmayan"] = taninmayan_
    if olculemedi: olcu["degersiz"] = olculemedi
    return sonuc(not taninmayan_, olcu)


def d13(ol, bag):
    b = [o for o in ol if o.get("olay") == "ajan_bitti"] or [o for o in (bag.get("tum") or []) if o.get("olay") == "ajan_bitti"]
    if not b: return sonuc(None, {}, "SubagentStop kaydı yok")
    ok = [o for o in b if o.get("dokum_var") and o.get("kullanim_satiri", 0) > 0]
    return sonuc(bool(ok), {"subagentstop": len(b), "dokum_yolu_geldi": any(o.get("dokum_var") for o in b),
                            "agent_transcript_path_alani": any(o.get("agent_dokum_alani") for o in b),
                            "kullanim_satiri": max([o.get("kullanim_satiri", 0) for o in b] or [0])})


def d14(ol, bag):
    eng = [o for o in ol if o.get("olay") == "stop" and o.get("engelledi")]
    if not eng: return sonuc(None, {}, "Stop engellemesi görülmedi (adım 14 kipi açık mı?)")
    devam = [n for n in (1, 2) if isaretler(ol, ad=f"stop-{n}", asama="bit")]
    aktif = [o.get("stop_hook_active") for o in ol if o.get("olay") == "stop" and "stop_hook_active" in o]
    return sonuc(len(devam) >= 1 and len(devam) >= min(2, len(eng)),
                 {"engelleme": len(eng), "devam_eden": len(devam), "stop_hook_active_dizisi": aktif[:6]})


def d15(ol, bag):
    e = bag.get("elle") or {}; oto = (bag.get("otomatik") or {}).get("15") or {}
    beklenen = oto.get("kodlar") or []
    if not beklenen: return sonuc(None, {}, "paket üretilmedi (o0a_kos.py adim 15)")
    if not e.get("kodlar"): return sonuc(None, {"beklenen": len(beklenen)}, "ajanın bildirdiği kodları kaydet --alan kodlar=K1,K2,… ile gir")
    gelen = {k.strip() for k in str(e["kodlar"]).split(",") if k.strip()}
    bulunan = sum(1 for k in beklenen if k in gelen)
    sik = [o for o in ol if o.get("olay") in ("ozet_once", "ozet_sonra") and o.get("agent_id")]
    return sonuc(bulunan == len(beklenen), {"beklenen": len(beklenen), "bulunan": bulunan, "token_tahmin": oto.get("token_tahmin"),
                                             "alt_ajan_sikistirma": bool(sik)})


def d17(ol, bag):
    tum = bag.get("tum") or ol; e = bag.get("elle") or {}
    var = {"SubagentStart": bool(olaylar_(tum, "ajan_basi")) or evet(e.get("SubagentStart", "")),
           "StopFailure": bool(olaylar_(tum, "hata")) or evet(e.get("StopFailure", "")),
           "PostCompact": bool(olaylar_(tum, "ozet_sonra")) or evet(e.get("PostCompact", "")),
           "PostModelSwitch": bool(olaylar_(tum, "model")) or evet(e.get("PostModelSwitch", ""))}
    if not var["SubagentStart"] and not var["PostCompact"] and not var["PostModelSwitch"]:
        return sonuc(None, var, "henüz olay yok: /compact, /model ve bir alt ajan çağrısı")
    eksik = [k for k, v in var.items() if not v]
    return sonuc(not eksik, dict(var, eksik=eksik))


def d18(ol, bag):
    k3 = [o for o in ol if o.get("olay") == "kod3_verdi"]; yb = [o for o in ol if o.get("olay") == "yavas_basladi" and o.get("giris") == "B"]
    if not (k3 and yb): return sonuc(None, {"kod3": bool(k3), "yavas": bool(yb)}, "iki işaretli komut da çalıştırılmalı")
    kod_gecti = bool(isaretler(ol, ad="kod3-b")); zaman_gecti = bool(isaretler(ol, ad="yavas-b"))
    return sonuc(not kod_gecti and not zaman_gecti, {"beklenmeyen_kod": "geciyor" if kod_gecti else "engelleniyor",
                                                     "zaman_asimi": "geciyor" if zaman_gecti else "engelleniyor"})


def d19(ol, bag):
    o = (bag.get("otomatik") or {}).get("19")
    if not o: return sonuc(None, {}, "`o0a_kos.py otomatik` koşulmadı")
    ok = bool(o.get("abonelik") and o.get("cikti_yazildi") and not o.get("dis_okundu") and not o.get("claude_md_yuklendi") and not o.get("bash_calisti"))
    return sonuc(ok, {k: o.get(k) for k in ("abonelik", "cikti_yazildi", "dis_okundu", "claude_md_yuklendi", "bash_calisti", "komut", "ortam_degiskenleri",
                                            "kullanici_claude_md_var", "hata")})


def d20(ol, bag):
    e = bag.get("elle") or {}
    if "bulut_kanca" not in e: return sonuc(None, {}, "bulut oturumunda gözlenir: kaydet 20 --alan bulut_kanca=evet|hayir --alan ortam_bulut=evet|hayir")
    k, b = evet(e["bulut_kanca"]), evet(e.get("ortam_bulut", ""))
    return sonuc(k and b, {"bulut_kanca_uygulandi": k, "ortam_bulut_ayirt": b})


I = "{I}"; K = "{K}"
KATALOG = [
    {"no": 1, "baslik": "CLAUDE_CODE_FORK_SUBAGENT=0 ile tek mesajdaki 3–5 Agent çağrısı paralel koşar ve ana Claude sonucu bekler",
     "adimlar": ["TEK mesajda 3 Agent çağrısı yap (subagent_type: o0a-sonda; arka plan YOK). İstemler: "
                 f"`{I} paralel-1 --bekle 20 {K}`, `… paralel-2 …`, `… paralel-3 …` komutunu Bash ile çalıştır.",
                 "Üçü bitince `o0a_kos.py degerlendir 1`."],
     "yedek": "Ajanlar sırayla çağrılır (ajan_paralel_max = 1); takvim olcek.py ile uzar.", "f": d1},
    {"no": 2, "baslik": "Arka planda biten alt ajanın bildirimi, ana tur bitmişken oturumu kendiliğinden uyandırır",
     "adimlar": [f"Agent (o0a-sonda, run_in_background: true) çağır; istem: `{I} arka-ajan --bekle 60 {K}` komutunu Bash ile çalıştır.",
                 "Hemen turunu BİTİR (yalnız 'bekliyorum' yaz; başka araç çağırma). Kullanıcı hiçbir şey yazmaz.",
                 "Oturum kendiliğinden uyanırsa `o0a_kos.py degerlendir 2`; 3 dk içinde uyanmazsa kullanıcı 'devam' yazar, sonra `o0a_kos.py degerlendir 2`."],
     "yedek": "Ana döngü arka plan ajanını beklemez: ajanlar ön planda koşar; sözleşme kartına \"her işten sonra 'tamam' yaz\" satırı (§4.2, §8.1).",
     "f": _arka_plan("arka-ajan")},
    {"no": 3, "baslik": "SubagentStop decision: block ile aşamalı devam (ön/arka plan); maxTurns'e ulaşan ajanda SubagentStop ve SendMessage ile sürdürme",
     "kip": {"ajan_bitti_engelle": {"ajan_tipi": "o0a-sonda", "neden": "O0A aşamalı devam: şimdi ikinci bölüm komutunu çalıştır (istemdeki ASAMA-2)."}},
     "adimlar": [f"Agent (o0a-sonda, ön plan) istemi: 'Önce `{I} asama-1 {K}` çalıştır ve bitir. Bitirmen engellenirse ASAMA-2: `{I} asama-2-on {K}`.'",
                 f"Agent (o0a-sonda, run_in_background: true) istemi aynı, ASAMA-2: `{I} asama-2-arka {K}`.",
                 f"Agent (o0a-sonda) istemi: '`{I} tur-1 {K}` … `{I} tur-10 {K}` komutlarını AYRI AYRI on Bash çağrısıyla çalıştır.' "
                 "(maxTurns 4: yarıda kesilmeli). Kesilince SendMessage ile aynı ajana 'kalan tur-N komutlarını çalıştır' yaz.",
                 "Sonra `o0a_kos.py degerlendir 3`."],
     "yedek": "Aşamalı devam yerine bölüm başına ayrı ajan görevi (film.py dilim); maxTurns'te kısmi çıktı film.py kurtar ile yeni göreve.", "f": d3},
    {"no": 4, "baslik": "PreToolUse Agent girdisinde subagent_type (fork dahil), name ve isolation görünür",
     "adimlar": [f"Agent çağır: subagent_type o0a-sonda (araçta varsa name 'o0a-ad'; isolation VERME: worktree origin/main ister, "
                 f"depoda yoksa başarısız olur); istem: `{I} ajan-4 {K}` çalıştır.",
                 "`o0a_kos.py degerlendir 4`. (Fork denenmez: CLAUDE_CODE_FORK_SUBAGENT=0 kalır. name/isolation karara girmez: sistem "
                 "kullanmaz.)"],
     "yedek": "Görünmeyen alan için kanca istemdeki görev yolundan bağlar; subagent_type yoksa ya da fork ise ajan kancası reddeder (D-10).", "f": d4},
    {"no": 5, "baslik": "onFailure: block ve timeout alanları komut kancasında çalışır (kasıtlı yavaş kanca)",
     "adimlar": [f"Bash: `{I} yavas-a O0A_YAVAS_A {K}` (A girişi 8 sn uyur; timeout 2, onFailure: block).",
                 "Komut engellenirse ya da çalışırsa fark etmez; sonra `o0a_kos.py degerlendir 5`."],
     "yedek": "Alan yoksa kanca.py'nin iç kapalı başarısızlığı tek güvencedir (D-11); kanca süresi ≤ 1 sn tutulur.", "f": d5},
    {"no": 6, "baslik": "Ayar env'i kanca süreçlerine geçer",
     "adimlar": [f"Bash: `{I} env-6 {K}` (herhangi bir Bash yeter).", "`o0a_kos.py degerlendir 6`."],
     "yedek": "Nabız ayar_sha yedeği: kanca.py fork_kapali settings dosyalarından okur (hazır).", "f": d6},
    {"no": 7, "baslik": "settings.local.json additionalDirectories ile veri köküne acceptEdits alt ajan soru sormadan yazar",
     "adimlar": ["Agent (o0a-sonda; permissionMode acceptEdits) istemi: '{YAZMA}/ajan_yazdi.txt dosyasına Write ile \"o0a\" yaz.'",
                 "İzin sorusu çıktı mı? Çıktıysa ONAYLAMA (reddet). `o0a_kos.py degerlendir 7` (gerekirse `kaydet 7 --alan soru_soruldu=evet|hayir`)."],
     "yedek": "settings.local.json permissions.allow'a Write/Edit(<veri>/FILMLER/**) kuralı; o da tutmazsa alt ajan depo içi geçici klasöre yazar, "
              "film.py CIKTI'ya kopyalar.", "f": d7},
    {"no": 8, "baslik": "Windows'ta Git Bash ile bash \"$CLAUDE_PROJECT_DIR/.claude/bin/kanca.sh\", PowerShell eşleyicisi, mutlak Python; kanca ≤ 2 sn",
     "adimlar": ["`o0a_kos.py otomatik` (gerçek kanca.sh ve kanca.py süresini 5'er kez ölçer).", f"Bash: `{I} bash-8 {K}`.",
                 "PowerShell aracı varsa onunla da bir komut çalıştır (ör. Get-Date).", "`o0a_kos.py degerlendir 8` (PowerShell yoksa `kaydet 8 --alan powershell=yok`)."],
     "yedek": "Kanca komutu bash'sız, mutlak Python ile doğrudan kanca.py (settings.local.json); PowerShell eşleyicisi yoksa yalnız Bash; "
              "süre aşılırsa tembel içe aktarma ve kanca bölünür.", "f": d8},
    {"no": 9, "baslik": "Becerideki hooks ile ayar kancası aynı komutu taşıyınca iki kez koşar mı",
     "adimlar": ["Kullanıcı /o0a-sonda yazar (beceri model tarafından çağrılamaz). Beceri bir O0A_CIFT komutu çalıştırır.", "`o0a_kos.py degerlendir 9`."],
     "yedek": "Beceri kancası ayar kancasıyla aynı komutu taşımaz (--kaynak beceri); kanca.py idempotent; beceri kancası koşmuyorsa ayar kancası tek güvence.",
     "f": d9},
    {"no": 10, "baslik": "Becerideki ! komutu Windows'ta Python'u bulur (|| true; py -3.10 yedeği)",
     "adimlar": ["9. adımdaki /o0a-sonda açılışı yeter (ön komutlar). `o0a_kos.py degerlendir 10`."],
     "yedek": "Beceri ve izin listesi komutları `py -3.10 .claude/bin/film.py …` biçimine çevrilir; settings.local.json env.PATH başına ana Python.",
     "f": d10},
    {"no": 11, "baslik": "claude --continue \"devam\" son oturumu sürdürür ve ilk mesajı gönderir (DEVAM.bat)",
     "adimlar": ["EN SONA bırak. Kullanıcı Claude Code'u kapatır; depo klasöründe terminalde `claude --continue \"devam\"` çalıştırır (ya da DEVAM.bat).",
                 "Açılan oturumda `o0a_kos.py degerlendir 11`."],
     "yedek": "DEVAM.bat yalnız `claude --continue` açar, kullanıcı 'devam' yazar (sözleşme kartı satırı).", "f": d11},
    {"no": 12, "baslik": "Ajan frontmatter (effort, omitClaudeMd, permissionMode, maxTurns) ve beceri alanları (disallowed-tools, allowed-tools, "
                         "disable-model-invocation, hooks) tanınır; tanınmayan alan sessizce yok sayılır",
     "adimlar": ["3, 7, 9 adımlarından sonra. Skill aracıyla o0a-sonda'yı çağırmayı dene (reddedilmeli) → `kaydet 12 --alan disable_model_invocation=evet|hayir`.",
                 "/o0a-sonda içinde isaret izin sormadan koştu mu → `--alan allowed_tools=evet|hayir`; WebFetch reddedildi mi → `--alan disallowed_tools=evet|hayir`.",
                 "effort: /agents ya da döküm başlığında görünüyor mu → `--alan effort=evet|hayir`. Sonra `o0a_kos.py degerlendir 12`."],
     "yedek": "Tanınmayan alanın işi kancaya ve film.py'ye: maxTurns → ajan_bitti kesmesi, omitClaudeMd → kör roller başsız claude -p, "
              "permissionMode → izin listesi, disallowed-tools → ajan tools listesi.", "f": d12},
    {"no": 13, "baslik": "SubagentStop girdisinde alt ajan döküm yolu gelir ve kullanım (token) satırları okunur (D-08)",
     "adimlar": ["Herhangi bir o0a-sonda çağrısından sonra `o0a_kos.py degerlendir 13`."],
     "yedek": "Token 'bilinmiyor': D-08 bütçesi ajan çağrısı sayısı × görev başı tahmin (olcek.py); model sapması yazılamaz.", "f": d13},
    {"no": 14, "baslik": "Stop kancası decision: block ile ana Claude'u sürmeye zorlar; ardışık sınır araç çağrısında sıfırlanır",
     "kip": {"stop_engelle": {"kalan": 2, "neden": "O0A devam kapısı {n}: şimdi Bash ile `{I} stop-{n} {K}` çalıştır, sonra turu bitir."}},
     "adimlar": ["Turunu bitir (Stop). Kanca iki kez engeller; her seferinde söylenen stop-N komutunu çalıştır.", "`o0a_kos.py degerlendir 14`."],
     "yedek": "Devam kapısı yoksa film-yap döngüsü her turda `film.py sonraki`yi kendisi çağırır; kullanıcı 'devam' yazar (DEVAM.bat).", "f": d14},
    {"no": 15, "baslik": "Alt ajan ≈ 0,2 M tokenlik izleme paketini tek oturumda okur; otomatik sıkıştırma tetiklenir mi",
     "hazirlik": "paket",
     "adimlar": ["Agent (general-purpose) istemi: '{PAKET} klasöründeki bütün parca_*.txt dosyalarını BAŞTAN SONA oku (gerekirse offset/limit ile); "
                 "her dosyada KOD-ile başlayan satırları topla ve yalnız virgüllü kod listesini döndür.'",
                 "Dönen listeyle: `o0a_kos.py kaydet 15 --alan kodlar=<liste>` ve `o0a_kos.py degerlendir 15`."],
     "yedek": "İzleme paketi ≤ 0,1 M token dilimlere bölünür (dilim.py), ajan aşamalı okur.", "f": d15},
    {"no": 16, "baslik": "Arka planda başlatılan Bash işinin (film.py bekle) bitmesi, ana tur bitmişken oturumu kendiliğinden uyandırır; en uzun süre",
     "adimlar": [f"Bash (run_in_background: true): `{I} arka-bash --bekle 90 {K}`. Hemen turunu BİTİR; kullanıcı hiçbir şey yazmaz.",
                 "Uyanınca (ya da 3 dk sonra kullanıcı 'devam' yazınca) `o0a_kos.py degerlendir 16`. İstersen daha uzun --bekle ile yinele."],
     "yedek": "Sözleşme kartına \"her işten sonra 'tamam' yaz\" satırı girer (§4.2, §8.1; [SON] O-4).", "f": _arka_plan("arka-bash")},
    {"no": 17, "baslik": "Dört olayın varlığı ve tetiklenmesi: SubagentStart, StopFailure, PostCompact, PostModelSwitch",
     "adimlar": ["/compact çalıştır; `/model` ile modeli değiştir ve geri al; bir alt ajan çağrısı yeter (SubagentStart).",
                 "StopFailure kendiliğinden tetiklenmez: /hooks listesinde görünüyorsa `kaydet 17 --alan StopFailure=listede`.", "`o0a_kos.py degerlendir 17`."],
     "yedek": "SubagentStart yerine film.py basla'nın yazdığı satır; PostCompact yerine SessionStart compact eşleyicisi; PostModelSwitch yerine "
              "SubagentStop dökümündeki model adı; StopFailure yoksa çalışan bağlar sonraki SessionStart'ta 'kesildi' sayılır.", "f": d17},
    {"no": 18, "baslik": "onFailure olmadan beklenmeyen kodla çıkan ve zaman aşımına uğrayan kanca: çağrı engelleniyor mu, geçiyor mu",
     "adimlar": [f"Bash: `{I} kod3-b O0A_KOD3_B {K}` (B girişi 3 koduyla çıkar).", f"Bash: `{I} yavas-b O0A_YAVAS_B {K}` (B girişi 8 sn uyur, timeout 2).",
                 "`o0a_kos.py degerlendir 18`."],
     "yedek": "kanca.sh beklenmeyen kodu güvenlik olaylarında 2'ye çevirir (hazır); zaman aşımı için güvenlik kancalarında onFailure: block (#5) ve kanca ≤ 1 sn.",
     "f": d18},
    {"no": 19, "baslik": "Başsız claude -p ile kör rol: abonelikle, CLAUDE.md ve bellek yüklenmeden, geçici klasör dışını okumadan, yalnız Read,Write",
     "adimlar": ["`o0a_kos.py otomatik` (geçici klasörde gerçek `claude -p` koşar; abonelik kullanır, kredi yok). Sonra `o0a_kos.py degerlendir 19`."],
     "yedek": "Kör görevler yalnız GIRDI kopyasıyla, talimat düzeyinde yalıtımla koşar; her rapor habersizlik: dogrulanmadi BAYRAK'ı taşır, M12 'ölçülemedi'.",
     "f": d19},
    {"no": 20, "baslik": "Bulut oturumunda depo kancaları uygulanır ve SessionStart ortam=bulut'u ayırt eder (D-45)",
     "adimlar": ["Bir BULUT geliştirme oturumunda: oturum başı bağlamında '[FİLM SETİ DURUMU · … ortam=bulut' satırı var mı?",
                 "Yerelde: `o0a_kos.py kaydet 20 --alan bulut_kanca=evet|hayir --alan ortam_bulut=evet|hayir` ve `o0a_kos.py degerlendir 20`."],
     "yedek": "Bulutta kanca yoksa bulut oturumu yalnız CLAUDE.md kuralıyla yürür (konu sorulmaz, film başlatılmaz); ortam ayrımı CLAUDE_CODE_REMOTE + os.name.",
     "f": d20},
]
NOLAR = [d["no"] for d in KATALOG]
ONERILEN_SIRA = [6, 8, 4, 1, 13, 3, 7, 5, 18, 9, 10, 12, 14, 2, 16, 15, 17, 19, 20, 11]


def madde(no):
    for d in KATALOG:
        if d["no"] == int(no): return d
    raise KeyError(f"davranış yok: {no}")
