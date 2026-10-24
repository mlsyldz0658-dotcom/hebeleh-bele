"""SONDA — Ö0-a deneme kancası (TASARIM §1.2 Ö0-a, §10.3, §4.5 `olcum0-a`). GEÇİCİDİR: yalnız `o0a_kos.py kur` ile kurulan
`.claude/settings.local.json`'da durur; `o0a_kos.py bitir` / `o0a_kos.py geri_al` onu kaldırır. Gerçek kancaların (kanca.py) yerine geçmez,
onlara EKLENİR (Claude Code iki ayar dosyasının kancalarını birlikte koşar); hiçbir güvenlik kuralını gevşetmez.

Kullanım (Claude Code çağırır; girdi stdin'de JSON):
  <python> o0a_sonda.py <olay> --giris <A|B|C|D|bash|mutlak|genel> --kayit <klasör>
  <python> o0a_sonda.py isaret <ad> [--bekle SN] --kayit <klasör>         (geliştirici Claude ya da alt ajan Bash ile çağırır)
Kayıt: <kayit>/olaylar.jsonl (satır başına bir olay). YAZILMAYANLAR: komut metni, istem metni, dosya içeriği, ortam değişkenlerinin
değerleri (yalnız O0A_SONDA_ENV ve CLAUDE_CODE_FORK_SUBAGENT değerleri; ikisi de gizli değildir), anahtar. Yalnız anahtar adları,
araç adı, O0A_* işaretleri, süreler ve sayılar yazılır.
Kip dosyası <kayit>/SONDA_KIP.json (o0a_kos.py adim yazar): ajan_bitti_engelle (SubagentStop decision: block, ajan başına bir kez),
stop_engelle (Stop decision: block, kalan sayısı kadar). Kip yoksa sonda HİÇBİR ŞEYİ ENGELLEMEZ (çıkış 0, çıktı yok).
İşaretli deneme komutları (yalnız komut metninde O0A_* işareti varsa): giriş A (onFailure: block, timeout 2) O0A_YAVAS_A → 8 sn uyur;
giriş B (onFailure yok, timeout 2) O0A_YAVAS_B → 8 sn uyur, O0A_KOD3_B → 3 koduyla çıkar.
Süre dolduysa (DENEME_DURUMU.json son_gecerlilik) ya da deneme kurulu değilse sonda edilgendir; SessionStart'ta süresi dolmuş denemeyi
`kos.geri_al` ile geri alır (çökme sonrası kendiliğinden geri alma).
Her beklenmeyen hata → çıkış 0 (sonda bilgi kancasıdır; oturumu bozmaz).
"""
import os, sys, json, time, re

BURASI = os.path.dirname(os.path.abspath(__file__))
SURUM = "sonda 1.0"
ISARET = re.compile(r"O0A_[A-Z0-9_]+")
CLAUDE_MD_IZI = ("YZ FİLM SETİ", "YZ F\\u0130LM SET\\u0130")     # kök CLAUDE.md başlığı (alt ajan bağlamında görünüyor mu, #12)
YAVAS_SN = 8


def _arg(argv, ad, vars_=None):
    return argv[argv.index(ad) + 1] if ad in argv and argv.index(ad) + 1 < len(argv) else vars_


def _json(p, vars_=None):
    try:
        with open(p, encoding="utf-8-sig") as f: return json.load(f)
    except (OSError, ValueError): return vars_


def _yaz_json(p, v):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(v, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def ekle(kayit, olay):
    """Tek satır, tek write (O_APPEND): eşzamanlı kancalar satır karıştırmaz."""
    os.makedirs(kayit, exist_ok=True)
    olay.setdefault("t", round(time.time(), 3)); olay.setdefault("pid", os.getpid())
    satir = (json.dumps(olay, ensure_ascii=False) + "\n").encode("utf-8")
    fd = os.open(os.path.join(kayit, "olaylar.jsonl"), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try: os.write(fd, satir)
    finally: os.close(fd)


def yaz_stdout(metin):
    """Kanca çıktısı HER ZAMAN UTF-8 bayt (Ö0-a #14: Windows'ta konsol kod sayfası cp1254/cp1252'ydi, Stop nedenindeki ü/ı/ş bozuldu).
    JSON zaten ensure_ascii ile yalnız ASCII; düz metin için de bayt yazılır."""
    b = metin.encode("utf-8")
    try: sys.stdout.buffer.write(b); sys.stdout.buffer.flush()
    except AttributeError: sys.stdout.write(metin); sys.stdout.flush()


def aktif(kayit):
    d = _json(os.path.join(kayit, "DENEME_DURUMU.json"), {}) or {}
    if d.get("durum") not in ("kurulu", "kuruluyor"): return False, d
    son = d.get("son_gecerlilik")
    return (son is None or time.time() <= float(son)), d


def ortam_izi():
    e = os.environ
    return {"O0A_SONDA_ENV": e.get("O0A_SONDA_ENV"), "CLAUDE_CODE_FORK_SUBAGENT": e.get("CLAUDE_CODE_FORK_SUBAGENT"),
            "proje_dizini_var": bool(e.get("CLAUDE_PROJECT_DIR")), "uzaktan_var": bool(e.get("CLAUDE_CODE_REMOTE")),
            "os": os.name}


def dokum_ozeti(p):
    """Alt ajan dökümü: kullanım satırı sayısı, token toplamları, CLAUDE.md izi. İçerik YAZILMAZ."""
    o = {"dokum_var": bool(p and os.path.isfile(p)), "kullanim_satiri": 0, "girdi": 0, "cikti": 0, "claude_md_gorundu": False,
         "model": None}
    if not o["dokum_var"]: return o
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            for sat in f:
                if not o["claude_md_gorundu"] and any(iz in sat for iz in CLAUDE_MD_IZI): o["claude_md_gorundu"] = True
                try: j = json.loads(sat)
                except ValueError: continue
                m = j.get("message") if isinstance(j, dict) else None
                if not isinstance(m, dict): continue
                u = m.get("usage") or {}
                if u:
                    o["kullanim_satiri"] += 1
                    o["girdi"] += int(u.get("input_tokens") or 0); o["cikti"] += int(u.get("output_tokens") or 0)
                if m.get("model"): o["model"] = str(m["model"])[:60]
    except OSError:
        o["dokum_var"] = False
    return o


# Oturuma kullanıcı yazmadan gelen istemler (arka plan işi bildirimi, sistem hatırlatması): #2/#16 kendiliğinden uyanma ölçümü
SISTEM_ISTEMI = re.compile(r"^\s*<(?:task-notification|system-reminder|bash-notification|background-task|agent-notification|"
                           r"local-command-stdout|command-name|bash-stdout)\b|<task-id>|<task-notification>", re.I)


def istem_turu(g):
    """UserPromptSubmit girdisi gerçek kullanıcı mesajı mı ("kullanici") yoksa sistemin ürettiği bildirim mi ("sistem")."""
    for k in ("isSynthetic", "is_synthetic", "isMeta", "is_meta"):
        if g.get(k) is True: return "sistem"
    koken = str(g.get("origin") or g.get("inbound_origin") or g.get("prompt_source") or "").lower()
    if koken and koken not in ("user", "kullanici", "human"): return "sistem"
    p = str(g.get("prompt") or "")
    if not p.strip() or SISTEM_ISTEMI.search(p[:4000]): return "sistem"
    return "kullanici"


def kip_al(kayit):
    return _json(os.path.join(kayit, "SONDA_KIP.json"), {}) or {}


def kip_yaz(kayit, k):
    _yaz_json(os.path.join(kayit, "SONDA_KIP.json"), k)


def kayit_kur(g, olay, giris):
    ti = g.get("tool_input") if isinstance(g.get("tool_input"), dict) else {}
    komut = str(ti.get("command") or "") if ti else ""
    o = {"olay": olay, "giris": giris, "hook": g.get("hook_event_name"), "session_id": g.get("session_id"),
         "agent_id": g.get("agent_id"), "agent_type": g.get("agent_type"), "tool_name": g.get("tool_name"),
         "tool_use_id": g.get("tool_use_id"), "girdi_anahtarlar": sorted(g.keys())[:40], "env": ortam_izi(),
         "claude_surum": os.environ.get("CLAUDE_CODE_VERSION")}
    if ti:
        o["ti_anahtarlar"] = sorted(ti.keys())[:40]
        if "subagent_type" in ti: o["subagent_type"] = str(ti.get("subagent_type"))[:60]
        o["name_var"] = "name" in ti; o["isolation_var"] = "isolation" in ti
        o["arka_plan"] = bool(ti.get("run_in_background"))
        if komut: o["isaretler"] = sorted(set(ISARET.findall(komut)))
        fp = ti.get("file_path") or ti.get("path")
        if fp: o["dosya_adi"] = os.path.basename(str(fp))[:80]
    if "effort" in g:                                   # Ö0-a #12: anahtar gelir ama değeri boş olabilir (None, "", {})
        e = g.get("effort")
        e = e.get("level") if isinstance(e, dict) else e
        o["effort_anahtari"] = True; o["effort"] = (str(e).strip()[:20] or None) if e not in (None, "") else None
    if g.get("source"): o["kaynak"] = str(g["source"])[:20]
    if "stop_hook_active" in g: o["stop_hook_active"] = bool(g.get("stop_hook_active"))
    if g.get("trigger"): o["tetik"] = str(g["trigger"])[:20]
    if olay == "istem":
        o["prompt_devam"] = str(g.get("prompt") or "").strip().lower() in ("devam", "devam et")
        o["istem_turu"] = istem_turu(g)                 # yalnız tür (kullanici | sistem); istem metni yazılmaz
    if olay == "bildirim": o["izin_mesaji"] = "permission" in str(g.get("message") or "").lower() or "izin" in str(g.get("message") or "").lower()
    if olay == "model":
        for a in ("model", "new_model", "previous_model", "old_model"):
            if g.get(a): o[a] = str(g[a])[:60]
    if olay == "ajan_bitti":
        o.update(dokum_ozeti(g.get("agent_transcript_path") or g.get("transcript_path")))
        o["agent_dokum_alani"] = "agent_transcript_path" in g
    return o, komut


def k_genel(argv):
    olay = argv[0]
    giris = _arg(argv, "--giris", "genel")
    kayit = _arg(argv, "--kayit") or os.environ.get("O0A_KAYIT")
    if not kayit: return 0
    bas = time.time()
    ok, durum = aktif(kayit)
    if not ok:
        if olay == "oturum_basi" and durum.get("durum") in ("kurulu", "kuruluyor"):
            try:
                sys.path.insert(0, BURASI)
                import o0a_kos as kos
                kos.geri_al(kayit=kayit, neden="süre doldu (SessionStart sondası)")
            except Exception:
                pass
        return 0
    ham = sys.stdin.buffer.read() if hasattr(sys.stdin, "buffer") else sys.stdin.read().encode("utf-8")
    try: g = json.loads(ham.decode("utf-8-sig", "replace")) if ham.strip() else {}
    except ValueError: g = {}
    if not isinstance(g, dict): g = {}
    o, komut = kayit_kur(g, olay, giris)
    sarmal = os.environ.get("O0A_SARMAL_BAS_NS")
    if sarmal and sarmal.isdigit(): o["sarmal_bas"] = int(sarmal) / 1e9
    cikti = None; kod = 0
    isaretler = set(o.get("isaretler") or ())
    if olay == "komut" and giris == "A" and "O0A_YAVAS_A" in isaretler:
        ekle(kayit, dict(o, olay="yavas_basladi")); time.sleep(YAVAS_SN); ekle(kayit, dict(o, olay="yavas_bitti")); return 0
    if olay == "komut" and giris == "B":
        if "O0A_YAVAS_B" in isaretler:
            ekle(kayit, dict(o, olay="yavas_basladi")); time.sleep(YAVAS_SN); ekle(kayit, dict(o, olay="yavas_bitti")); return 0
        if "O0A_KOD3_B" in isaretler:
            ekle(kayit, dict(o, olay="kod3_verdi")); return 3
    if olay == "ajan_bitti":
        k = kip_al(kayit); e = k.get("ajan_bitti_engelle") or {}
        aid = str(g.get("agent_id") or "")
        if e and aid and aid not in (e.get("engellenen") or []) and (not e.get("ajan_tipi") or e["ajan_tipi"] == g.get("agent_type")):
            e.setdefault("engellenen", []).append(aid); k["ajan_bitti_engelle"] = e; kip_yaz(kayit, k)
            cikti = {"decision": "block", "reason": e.get("neden") or "O0A aşamalı devam sınaması: ikinci bölüme geç."}
            o["engelledi"] = True
    if olay == "stop" and not g.get("agent_id"):
        k = kip_al(kayit); e = k.get("stop_engelle") or {}
        if int(e.get("kalan") or 0) > 0:
            e["kalan"] = int(e["kalan"]) - 1; e["verilen"] = int(e.get("verilen") or 0) + 1; k["stop_engelle"] = e; kip_yaz(kayit, k)
            cikti = {"decision": "block", "reason": (e.get("neden") or "O0A devam kapısı sınaması.").replace("{n}", str(e["verilen"]))}
            o["engelledi"] = True; o["engel_no"] = e["verilen"]
    o["sure_ms"] = round((time.time() - bas) * 1000, 1)
    if o.get("sarmal_bas"): o["sarmal_sure_ms"] = round((time.time() - o["sarmal_bas"]) * 1000, 1)
    ekle(kayit, o)
    if cikti is not None: yaz_stdout(json.dumps(cikti, ensure_ascii=True))
    return kod


def k_isaret(argv):
    ad = argv[1] if len(argv) > 1 and not argv[1].startswith("--") else "isimsiz"
    kayit = _arg(argv, "--kayit") or os.environ.get("O0A_KAYIT")
    if not kayit: print("!! --kayit yok"); return 4
    bekle = float(_arg(argv, "--bekle", "0") or 0)
    o = {"olay": "isaret", "ad": re.sub(r"[^\w.\-]", "_", ad)[:60], "env": ortam_izi(),
         "ajan_ortami": bool(os.environ.get("CLAUDE_AGENT_ID") or os.environ.get("CLAUDE_CODE_AGENT_ID"))}
    ekle(kayit, dict(o, asama="bas"))
    if bekle > 0: time.sleep(min(bekle, 7200))
    ekle(kayit, dict(o, asama="bit", bekle_sn=bekle))
    yaz_stdout("O0A işaret: %s (%s sn)\n" % (o["ad"], bekle))
    return 0


def main(argv):
    if not argv: print(__doc__); return 0
    try:
        if argv[0] == "isaret": return k_isaret(argv)
        return k_genel(argv)
    except Exception as e:                         # sonda bilgi kancasıdır: oturumu asla bozmaz
        try:
            k = _arg(argv, "--kayit") or os.environ.get("O0A_KAYIT")
            if k: ekle(k, {"olay": "sonda_hatasi", "hata": type(e).__name__})
        except Exception:
            pass
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
