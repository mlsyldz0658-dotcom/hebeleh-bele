"""BECERİ DENETİM — 4 beceri, 21 ajan, görev şablonları ve şemaların denetimi + §4.8 senaryoları (TASARIM §3.1, §4, §6.2, §9 adım 6).

Kullanım:
  python beceri_denetim.py [--json] [--rapor <yol.json>] [--kati] [--depo <depo kökü>]
        Statik denetim: SKILL.md'ler (frontmatter, ad, açıklama uzunluğu, satır ve çekirdek token sınırı, tek soru metni, referans dosyaları,
        film.py komutları, kancalar), §4.6 klasör düzeni, reference/ (≤ 300 satır, içindekiler, kural taşımaz), ajan dosyaları (ad = ADLAR,
        model/effort/permissionMode, araçlar role göre, kör ajanda omitClaudeMd, memory yok, açıklama kalıbı ve toplamı), sablonlar/ (ad
        kuralı, hat/asamalar.py'deki her ajan görevine şablon, {{esik:<anahtar>}} yer tutucuları, OZET biçimi, kör şablonda sızıntı),
        semalar/ (geçerli JSON Schema, zorunlu şemalar), kök CLAUDE.md (tek soru ve bulut cümlesi), kullanıcıya konu dışında soru.
  python beceri_denetim.py --senaryo hepsi|1,2,… [--json]
        §4.8 senaryoları 1–7: geçici veri kökünde, sahte sağlayıcıyla, ağsız ve kredisiz; film.py ve kanca.py gerçek süreç olarak çalışır.
  python beceri_denetim.py --sablon <A07b_yonetmen_plan.md> [--ayar FILM_AYAR.json]   şablonu eşiklerle doldurup basar
  python beceri_denetim.py --hat-yenile        reference/hat.md'nin aşama tablosunu hat/asamalar.py'den yeniden yazar
  film.py içinden: python .claude/bin/film.py beceri-denetim [aynı seçenekler]
Kodda:
  import beceri_denetim as bd
  bd.denetle(depo=None) → {"sonuc", "ozet", "maddeler": [{madde, seviye, dosya, neden}]}
  bd.sablon_doldur(metin, E=None) → yer tutucuları basılmış metin (film.py ISTEM.md'yi yazarken çağırır; bilinmeyen anahtar → SablonHatasi)
  bd.senaryolar([1, 2], depo=None) → [{no, ad, sonuc, adimlar}]
Çıkış kodları: 0 HATA yok · 1 HATA var (--kati ile BAYRAK da 1) · 4 ORTAM (depo ya da gerekli dosya yok).
Bu araç hiçbir dosyayı değiştirmez (--hat-yenile ve --rapor dışında); anahtar dosyalarını okumaz; senaryolar yalnız geçici klasörde yazar.
"""
import os, sys, re, json, math, glob, time, shutil, hashlib, tempfile, subprocess, importlib.util
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)

SURUM = "beceri_denetim 1.0"
TEK_SORU = ("Filmin konusu ne olsun? Bir cümle yeter (ör. ejderha yavrusunu saklayan avcı kadın). "
            "İstersen 'sen seç' yaz.")
BULUT_CUMLESI = "Film seti senin bilgisayarında çalışır: Masaüstündeki FILM_SETI.bat'a çift tıkla ve konuyu orada yaz."
BECERILER = ("film-yap", "film-durum", "film-not", "film-gelistir")
SATIR_MAX = {"film-yap": 250, "film-durum": 60, "film-not": 120, "film-gelistir": 150}   # §4.2–§4.5 (gövde)
CEKIRDEK_TOKEN_MAX = 4500
CEKIRDEK_SATIR_HEDEF = 110
CEKIRDEK_SONU = "--- (çekirdek sonu) ---"
ACIKLAMA_KR_MAX = 1536            # Claude Code beceri listesinde description + when_to_use kesilme sınırı
AJAN_ACIKLAMA_TOKEN_HEDEF = 3000  # §3.1 kural 3 (hedef, tahmin)
AJAN_ACIKLAMA_TOKEN_UYARI = 15000
REFERANS_SATIR_MAX = 300
REFERANS_ICINDEKILER_SATIR = 100
SABLON_SATIR_MAX = 120
DUZEN = ("SKILL.md", "KURTARMA.md", "GOREV_SEMASI.md", "KULLANICI_DILI.md", "PLAN_DILI.md", "sablonlar", "semalar", "reference")
REFERANSLAR = ("hat.md", "hikaye_odasi.md", "yonetmen.md", "goruntu_sureklilik.md", "ses.md", "kurgu.md", "yayin.md")
ZORUNLU_SEMALAR = ("gorev_v2", "kapi_rapor_v1", "seyirci_rapor_v2", "juri_v1", "ozet_eslesme_v1", "denetci_rapor_v1", "kuyruk_madde_v1")
DIS_SEMALAR = ("plan_v2",)        # yönetmen kâğıdının sahibi yazar (adım 8); yoksa BAYRAK
BECERI_DOSYALARI = ("KURTARMA.md", "GOREV_SEMASI.md", "KULLANICI_DILI.md", "PLAN_DILI.md", "ZANAAT.md", "BILGI_KURALLARI.md")
KURTARMA_BOLUMLERI = ("Kanca", "Kilit", "DUR", "Kesik görev", "Kesik indirme", "GPU", "Kullanım sınırı", "Flow kilidi", "Disk")
OLCUTLER = ("anlasilirlik", "akicilik", "merak", "duygu", "ritim", "ilk30")
ROL_ARACLARI = {"yazar": {"Read", "Write", "Edit", "Glob", "Grep"}, "denetci": {"Read", "Write", "Glob", "Grep"}, "kor": {"Read", "Write"}}
YENI_DOSYA_YAZARLARI = ("ders-editoru", "memmet-bakimci")     # §3.1: Edit yok
YASAK_ARACLAR = re.compile(r"^(Bash|PowerShell|Agent|Task|WebFetch|WebSearch|NotebookEdit|MultiEdit|mcp__.*|Skill|SendMessage)$")
MAX_TURNS = {"yazar": 100, "denetci": 60, "kor": 60, "yonetmen": 80, "hikaye-yazari": 80, "kurgucu": 80, "kare-tarifcisi": 40}
ACIKLAMA_KALIBI = "Yalnız film.py görev defteri"

# Kullanıcıya konu dışında soru (KK1). Olumsuzlayan satır (YOK, yasak, sorulmaz …) serbesttir: kural metni yasağı anlatır.
SORU_YASAK = re.compile(r"hangisini istersin|onaylıyor musun|onaylar mısın|devam edeyim mi|devam edelim mi|ister misin|istiyor musun|"
                        r"tercih eder misin|kullanıcıya sor\b|kullanıcıya soru sor|kullanıcıya danış|kullanıcıdan onay|kullanıcının onayını|"
                        r"kullanıcıya seçenek sun|ask the user|which one do you", re.I)
OLUMSUZ = re.compile(r"\b(YOK|yok|yasak\w*|YASAK|sorulmaz|sorma\w*|değil|engeller|reddeder|reddedilir|asla|ASLA|hiç|hiçbir|verilmez|"
                     r"okunmaz|yapılmaz|kullanılmaz|çağrılmaz|eklenmez|istenmez|sunma|isteme|never|not)\b")
TEHLIKE = re.compile(r"robocopy\s+\S.*?/MIR|rm\s+-rf|git\s+push|Remove-Item\s+.*-Recurse|del\s+/s", re.I)
GIZLI = re.compile(r"(AYARLAR[\\/]\S*(anahtar|\.env|telegram|memmet_profil))|_anahtar\.txt|telegram_bot\.txt", re.I)
KOR_SIZINTI = re.compile(r"SAHNELER|HIKAYE\.json|_HIKAYE_ODASI|_YONETMEN|DERSLER|\bamac\b|KARAR_DEFTERI")
YER_TUTUCU = re.compile(r"\{\{\s*([^{}]*?)\s*\}\}")
OZET_SATIRI = re.compile(r"OZET \|[^`\n]*")
OZET_BICIM = re.compile(r"^OZET( \| [A-Za-z0-9_]+: [^|]+)+$")


class SablonHatasi(Exception):
    pass


# ---- yardımcılar --------------------------------------------------------------------------------------------------
def simdi(): return time.strftime("%Y-%m-%dT%H:%M:%S")


def oku(yol):
    """Satır sonu \n'e çevrilir: Windows'ta git (core.autocrlf) depoyu CRLF ile açar."""
    with open(yol, "rb") as f: return f.read().decode("utf-8-sig", "replace").replace("\r\n", "\n")


def json_oku(yol, vars_=None):
    try:
        with open(yol, encoding="utf-8-sig") as f: return json.load(f)
    except (OSError, ValueError): return vars_


def atomik_yaz(yol, veri):
    os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
    gec = yol + ".yazılıyor"
    with open(gec, "w", encoding="utf-8", newline="\n") as f:
        f.write(veri if isinstance(veri, str) else json.dumps(veri, ensure_ascii=False, indent=1) + "\n")
    os.replace(gec, yol)


def token_tahmin(metin): return int(math.ceil(len(metin) / 3.5))       # tahmin (Türkçe metin; ölçülmedi)


def depo_bul(depo=None):
    return os.path.abspath(depo) if depo else os.path.dirname(os.path.dirname(HERE))


def olumsuz(satir): return bool(OLUMSUZ.search(satir))


def _skaler(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
        return v.replace('\\"', '"') if v else v
    if v in ("true", "True"): return True
    if v in ("false", "False"): return False
    if v in ("null", "~", ""): return None if v else ""
    if re.fullmatch(r"-?\d+", v): return int(v)
    if v.startswith("[") and v.endswith("]"): return [_skaler(x) for x in v[1:-1].split(",") if x.strip()]
    return v


def on_bilgi(metin):
    """YAML frontmatter'ın küçük alt kümesi: üst düzey anahtarlar, >-/| blokları, '- ' listeleri; iç içe bloklar ham metin.
    (gövde, sözlük, hata) döner; frontmatter yoksa sözlük None."""
    sat = metin.split("\n")
    if not sat or sat[0].strip() != "---": return metin, None, "frontmatter yok"
    try: son = next(i for i in range(1, len(sat)) if sat[i].strip() == "---")
    except StopIteration: return metin, None, "frontmatter kapanmıyor"
    d, i, fm = {}, 1, sat[1:son]
    while i - 1 < len(fm):
        s = fm[i - 1]
        if not s.strip() or s.lstrip().startswith("#"): i += 1; continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", s)
        if not m: return "\n".join(sat[son + 1:]), d, "çözülemeyen satır: %r" % s[:60]
        k, v = m.group(1), m.group(2)
        blok = []
        j = i
        while j < len(fm) and (fm[j].startswith((" ", "\t")) or not fm[j].strip()):
            blok.append(fm[j]); j += 1
        if v.strip() in (">-", ">", "|", "|-"):
            parca = [b.strip() for b in blok if b.strip()]
            d[k] = (" " if v.strip().startswith(">") else "\n").join(parca)
        elif v.strip() == "":
            dolu = [b for b in blok if b.strip()]
            if dolu and all(b.strip().startswith("- ") for b in dolu): d[k] = [_skaler(b.strip()[2:]) for b in dolu]
            else: d[k] = {"_ham": "\n".join(blok)}
        else:
            d[k] = _skaler(v)
        i = j + 1
    return "\n".join(sat[son + 1:]), d, None


def arac_listesi(v):
    if v is None: return None
    if isinstance(v, list): return [str(x).strip() for x in v if str(x).strip()]
    return [x.strip() for x in str(v).split(",") if x.strip()]


def esikleri_yukle(depo, ayar=None):
    ar = os.path.join(depo, "YZ_FILM", "ARACLAR")
    if ar not in sys.path: sys.path.insert(0, ar)
    import esikler
    return esikler.yukle(ayar=ayar) if ayar else esikler.yukle()


def _modul(ad, yol):
    sp = importlib.util.spec_from_file_location(ad, yol); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def hat_modulu(depo):
    ar = os.path.join(depo, "YZ_FILM", "ARACLAR")
    if ar not in sys.path: sys.path.insert(0, ar)
    import hat.asamalar as H
    return H


def deger_metni(v):
    if isinstance(v, bool): return "evet" if v else "hayır"
    if isinstance(v, float): return ("%g" % v).replace(".", ",")
    if isinstance(v, (list, tuple)):
        if len(v) == 2 and all(isinstance(x, (int, float)) for x in v): return "%s–%s" % (deger_metni(v[0]), deger_metni(v[1]))
        return ", ".join(deger_metni(x) for x in v)
    if isinstance(v, dict): return json.dumps(v, ensure_ascii=False)
    if v is None: return "ölçülmedi"
    return str(v)


def sablon_doldur(metin, E=None, depo=None):
    """{{esik:<anahtar>}} → eşik değeri (Türkçe sayı biçimi). Bilinmeyen anahtar ya da başka yer tutucu → SablonHatasi."""
    if E is None: E = esikleri_yukle(depo_bul(depo))
    def bas(m):
        ic = m.group(1)
        if not ic.startswith("esik:"): raise SablonHatasi("bilinmeyen yer tutucu: {{%s}}" % ic)
        k = ic[5:].strip()
        if k not in E: raise SablonHatasi("eşik dosyalarında olmayan anahtar: %s" % k)
        return deger_metni(E[k])
    return YER_TUTUCU.sub(bas, metin)


# ---- denetim ------------------------------------------------------------------------------------------------------
class Denetim:
    def __init__(self, depo):
        self.depo = depo; self.maddeler = []
        self.beceri = os.path.join(depo, ".claude", "skills")
        self.fy = os.path.join(self.beceri, "film-yap")
        self.ajan_dir = os.path.join(depo, ".claude", "agents")
        self.adlar = json_oku(os.path.join(depo, "YZ_FILM", "ARACLAR", "veri", "ADLAR.json"), {}) or {}
        self._E = None; self._H = None

    def m(self, madde, seviye, dosya, neden):
        self.maddeler.append({"madde": madde, "seviye": seviye, "dosya": self.rel(dosya) if dosya else None, "neden": neden})

    def rel(self, p):
        try: return os.path.relpath(p, self.depo)
        except ValueError: return p                       # Windows: başka sürücüdeki yol (C: / D:) göreli yazılamaz

    @property
    def E(self):
        if self._E is None:
            try: self._E = esikleri_yukle(self.depo)
            except Exception as e:
                self._E = {}; self.m("esikler", "BAYRAK", None, "eşik dosyaları yüklenemedi: %s" % e)
        return self._E

    @property
    def H(self):
        if self._H is None:
            try: self._H = hat_modulu(self.depo)
            except Exception as e:
                self._H = False; self.m("asamalar", "BAYRAK", None, "hat/asamalar.py yüklenemedi: %s" % e)
        return self._H

    def kadro(self): return {k: v for k, v in (self.adlar.get("ajanlar") or {}).items() if not k.startswith("_")}

    # -- metin denetimleri (her .md için)
    def soru_tarama(self, yol, metin, kim):
        for n, s in enumerate(metin.split("\n"), 1):
            t = s.replace(TEK_SORU, " ").replace(BULUT_CUMLESI, " ")
            if SORU_YASAK.search(t) and not olumsuz(t):
                self.m("konu_disi_soru", "HATA", yol, "%s satır %d: kullanıcıya karar/onay sorusu (KK1): %r" % (kim, n, s.strip()[:90]))
            if TEHLIKE.search(t) and not olumsuz(t):
                self.m("tehlikeli_komut", "HATA", yol, "%s satır %d: kalıcı silme/robocopy/push talimatı: %r" % (kim, n, s.strip()[:90]))
            if GIZLI.search(t) and not olumsuz(t):
                self.m("gizli_dosya", "HATA", yol, "%s satır %d: anahtar dosyasına yönelik talimat" % (kim, n))

    # -- beceriler
    def beceriler(self):
        if not os.path.isdir(self.beceri):
            self.m("beceri_klasoru", "HATA", self.beceri, ".claude/skills yok"); return
        adlar = set((self.adlar.get("beceriler") or {}).keys()) or set(BECERILER)
        var = {d for d in os.listdir(self.beceri) if os.path.isdir(os.path.join(self.beceri, d))}
        for d in sorted(var - adlar): self.m("beceri_adi", "HATA", os.path.join(self.beceri, d), "ADLAR.json'da olmayan beceri: %s" % d)
        for ad in BECERILER:
            p = os.path.join(self.beceri, ad, "SKILL.md")
            if not os.path.isfile(p): self.m("beceri_yok", "HATA", p, "SKILL.md yok"); continue
            self.beceri_dosyasi(ad, p)
        self.duzen(); self.referanslar(); self.kurtarma_bolumleri(); self.kullanici_dili()

    def beceri_dosyasi(self, ad, p):
        metin = oku(p); govde, fm, hata = on_bilgi(metin)
        if fm is None: self.m("frontmatter", "HATA", p, hata); return
        if hata: self.m("frontmatter", "HATA", p, hata)
        if fm.get("name") != ad: self.m("beceri_adi", "HATA", p, "name (%r) klasör adı değil (%s)" % (fm.get("name"), ad))
        if not re.fullmatch(r"[a-z0-9-]{1,64}", str(fm.get("name") or "")): self.m("beceri_adi", "HATA", p, "ad kuralı: küçük harf, rakam, tire")
        acik = str(fm.get("description") or ""); ne_zaman = str(fm.get("when_to_use") or "")
        if len(acik) < 40: self.m("aciklama", "HATA", p, "description boş ya da çok kısa")
        if len(acik) + len(ne_zaman) > ACIKLAMA_KR_MAX:
            self.m("aciklama_uzun", "HATA", p, "description + when_to_use %d kr > %d (listede kesilir)" % (len(acik) + len(ne_zaman), ACIKLAMA_KR_MAX))
        dmi = fm.get("disable-model-invocation") is True
        if ad == "film-gelistir" and not dmi: self.m("model_acamaz", "HATA", p, "film-gelistir disable-model-invocation: true taşımalı (§4.5)")
        if ad != "film-gelistir" and dmi: self.m("model_acamaz", "HATA", p, "%s Claude tarafından açılabilmeli (§4.1)" % ad)
        izin = arac_listesi(fm.get("allowed-tools")) or []
        for x in izin:
            if not re.fullmatch(r"Bash\(python \.claude/bin/film\.py [^()]*\)", x):
                self.m("izinli_arac", "HATA", p, "allowed-tools yalnız 'Bash(python .claude/bin/film.py …)' olabilir: %s" % x)
        if ad == "film-durum":
            yasak = set(arac_listesi(fm.get("disallowed-tools")) or [])
            eksik = {"Write", "Edit", "NotebookEdit", "Agent"} - yasak
            if eksik: self.m("film_durum_yazmaz", "HATA", p, "disallowed-tools eksik: %s" % ", ".join(sorted(eksik)))
        sat = govde.strip("\n").split("\n")
        if len(sat) > SATIR_MAX[ad]: self.m("beceri_satir", "HATA", p, "gövde %d satır > %d" % (len(sat), SATIR_MAX[ad]))
        if ad == "film-yap": self.film_yap(p, fm, govde)
        self.soru_tarama(p, govde, ad)
        self.komutlar(p, metin)
        self.dosya_atiflari(p, metin)

    def film_yap(self, p, fm, govde):
        if CEKIRDEK_SONU not in govde: self.m("cekirdek", "HATA", p, "çekirdek sonu işareti yok (%s)" % CEKIRDEK_SONU)
        cek = govde.split(CEKIRDEK_SONU)[0]
        t = token_tahmin(cek); n = len(cek.strip("\n").split("\n"))
        if t > CEKIRDEK_TOKEN_MAX: self.m("cekirdek_token", "HATA", p, "çekirdek ≈ %d token > %d (tahmin)" % (t, CEKIRDEK_TOKEN_MAX))
        if n > CEKIRDEK_SATIR_HEDEF: self.m("cekirdek_satir", "BAYRAK", p, "çekirdek %d satır > ≈ %d" % (n, CEKIRDEK_SATIR_HEDEF))
        if TEK_SORU not in govde: self.m("tek_soru", "HATA", p, "tek soru metni harfiyen yok (§4.1)")
        if BULUT_CUMLESI not in govde: self.m("bulut_cumlesi", "HATA", p, "bulut bilgi cümlesi harfiyen yok (D-45)")
        kurallar = re.findall(r"^(\d+)\. ", govde.split("## 2.")[0].split("## 1.")[-1], re.M)
        if [int(x) for x in kurallar] != list(range(1, 13)): self.m("degismez_kurallar", "HATA", p, "§1'de 12 değişmez kural yok (%d)" % len(kurallar))
        if "--saglayici sahte" not in govde: self.m("bulut_sahte", "BAYRAK", p, "bulutta yalnız --saglayici sahte denemesi yazılı değil")
        ham = (fm.get("hooks") or {}).get("_ham", "") if isinstance(fm.get("hooks"), dict) else ""
        for olay in ("erisim", "komut", "ajan"):
            if not re.search(r"kanca\.sh\\?\"?\s+%s\b" % olay, ham): self.m("beceri_kancasi", "HATA", p, "PreToolUse %s kancası yok (§4.2)" % olay)
        if not os.path.isfile(os.path.join(self.depo, ".claude", "bin", "kanca.sh")):
            self.m("kanca_sh", "HATA", os.path.join(self.depo, ".claude", "bin"), "kanca.sh yok")
        if not os.path.isfile(os.path.join(self.depo, ".claude", "bin", "film.py")):
            self.m("film_sarmalayici", "HATA", os.path.join(self.depo, ".claude", "bin"), ".claude/bin/film.py yok")

    def film_komutlari(self):
        f = os.path.join(self.depo, "YZ_FILM", "ARACLAR", "film.py")
        m = re.search(r"KOMUTLAR\s*=\s*\((.*?)\)", oku(f), re.S) if os.path.isfile(f) else None
        return set(re.findall(r"\"([a-z-]+)\"", m.group(1))) if m else set()

    def komutlar(self, p, metin):
        k = self.film_komutlari()
        if not k: return
        bulunan = re.findall(r"python3?\s+\S*film\.py\s+([a-z][a-z-]*)", metin) + re.findall(r"`film\.py\s+([a-z][a-z-]*)", metin)
        for c in sorted(set(bulunan)):
            if c not in k: self.m("film_komutu", "HATA", p, "film.py'de olmayan komut: %s" % c)

    def dosya_atiflari(self, p, metin):
        taban = os.path.dirname(p)
        for r in sorted(set(re.findall(r"(?:\.\./film-yap/)?reference/[a-z_]+\.md", metin))):
            hedef = os.path.normpath(os.path.join(taban, r)) if r.startswith("..") else os.path.join(self.fy, r)
            if not os.path.isfile(hedef): self.m("atif", "HATA", p, "atıf yapılan dosya yok: %s" % r)
        for ad in BECERI_DOSYALARI:
            if re.search(r"(?<![\w/])%s" % re.escape(ad), metin) and not os.path.isfile(os.path.join(self.fy, ad)):
                self.m("atif", "HATA", p, "atıf yapılan beceri dosyası yok: %s" % ad)
        for r in sorted(set(re.findall(r"(?<![\w/<.])((?:YZ_FILM|\.claude)/[A-Za-z0-9_./-]+)", metin))):
            r = r.rstrip(".,;:)`'\"")
            if "<" in r or "*" in r: continue
            if not os.path.exists(os.path.join(self.depo, r)): self.m("atif_depo", "BAYRAK", p, "depoda henüz yok: %s" % r)
        for b in sorted(set(re.findall(r"KURTARMA\.md §([A-Za-zÇĞİÖŞÜçğıöşü ]+?)(?=[\s;'.,)]|$)", metin))):
            self.kurtarma_bolum_var(p, b)

    def kurtarma_bolum_var(self, p, b):
        k = os.path.join(self.fy, "KURTARMA.md")
        if not os.path.isfile(k): return
        if not re.search(r"^## §%s\b" % re.escape(b.strip()), oku(k), re.M):
            self.m("kurtarma_bolumu", "HATA", p, "KURTARMA.md'de §%s bölümü yok" % b.strip())

    def duzen(self):
        for d in DUZEN:
            if not os.path.exists(os.path.join(self.fy, d)): self.m("duzen", "HATA", os.path.join(self.fy, d), "§4.6 düzeninde var olmalı")
        for r in REFERANSLAR:
            if not os.path.isfile(os.path.join(self.fy, "reference", r)): self.m("duzen", "HATA", os.path.join(self.fy, "reference", r), "reference dosyası yok")

    def referanslar(self):
        for p in sorted(glob.glob(os.path.join(self.fy, "reference", "*.md"))):
            t = oku(p); s = t.rstrip("\n").split("\n")
            if len(s) > REFERANS_SATIR_MAX: self.m("referans_satir", "HATA", p, "%d satır > %d" % (len(s), REFERANS_SATIR_MAX))
            if len(s) > REFERANS_ICINDEKILER_SATIR and not any("İçindekiler" in x for x in s[:12]):
                self.m("referans_icindekiler", "HATA", p, "100 satırı aşan referansın başında içindekiler yok")
            if re.search(r"KESİN KURAL|^\s*KURAL:", t, re.M): self.m("referans_kural", "BAYRAK", p, "reference/ kural taşımaz (§4.6)")
            self.soru_tarama(p, t, "reference")
        for p in (os.path.join(self.fy, x) for x in ("KURTARMA.md", "GOREV_SEMASI.md", "KULLANICI_DILI.md", "PLAN_DILI.md")):
            if os.path.isfile(p):
                t = oku(p); self.soru_tarama(p, t, os.path.basename(p)); self.komutlar(p, t); self.dosya_atiflari(p, t)
        self.hat_tazelik()

    def kurtarma_bolumleri(self):
        p = os.path.join(self.fy, "KURTARMA.md")
        if not os.path.isfile(p): return
        t = oku(p)
        for b in KURTARMA_BOLUMLERI:
            if not re.search(r"^## §%s\b" % re.escape(b), t, re.M): self.m("kurtarma_bolumu", "HATA", p, "§%s yok (§4.2)" % b)
        for kaynak in (os.path.join(self.depo, "YZ_FILM", "ARACLAR", "film.py"), os.path.join(self.depo, ".claude", "hooks", "kanca.py")):
            if os.path.isfile(kaynak):
                for b in set(re.findall(r"KURTARMA\.md §([A-Za-z]+)", oku(kaynak))): self.kurtarma_bolum_var(kaynak, b)

    def kullanici_dili(self):
        p = os.path.join(self.fy, "KULLANICI_DILI.md")
        if not os.path.isfile(p): return
        t = oku(p)
        for k in range(9):
            if not re.search(r"^\| %d \|" % k, t, re.M): self.m("cikis_cumlesi", "HATA", p, "çıkış kodu %d için cümle satırı yok" % k)
        if TEK_SORU not in t: self.m("tek_soru", "HATA", p, "tek soru metni harfiyen yok")
        if BULUT_CUMLESI not in t: self.m("bulut_cumlesi", "HATA", p, "bulut cümlesi harfiyen yok")

    def hat_tablosu(self):
        H = self.H
        if not H: return None
        return [l for l in H.markdown().strip().split("\n") if not l.startswith("# ")]

    def hat_tazelik(self):
        p = os.path.join(self.fy, "reference", "hat.md")
        if not os.path.isfile(p): return
        t = oku(p); m = re.search(r"<!-- hat\.asamalar:bas -->\n(.*?)\n<!-- hat\.asamalar:son -->", t, re.S)
        if not m: self.m("hat_tablosu", "BAYRAK", p, "üretilmiş tablo işaretleri yok"); return
        tab = self.hat_tablosu()
        if tab is not None and [x for x in m.group(1).split("\n") if x.strip()] != [x for x in tab if x.strip()]:
            self.m("hat_tablosu", "BAYRAK", p, "aşama tablosu hat/asamalar.py ile aynı değil (beceri_denetim.py --hat-yenile)")

    # -- ajanlar
    def ajanlar(self):
        kadro = self.kadro()
        if not os.path.isdir(self.ajan_dir): self.m("ajan_klasoru", "HATA", self.ajan_dir, "yok"); return
        dosyalar = {os.path.splitext(os.path.basename(p))[0]: p for p in glob.glob(os.path.join(self.ajan_dir, "*.md"))}
        eski = set((self.adlar.get("ajanlar_eski") or {}).keys()) - {"_aciklama"}
        kalkan = set((self.adlar.get("ajan_adlari_kalkan") or {}).keys()) - {"_aciklama"}
        for ad, p in sorted(dosyalar.items()):
            if ad in eski: self.m("eski_ajan", "HATA", p, "§3.2: depodan kaldırılacak taslak (.claude/_ESKI/agents/'e taşı)")
            elif ad in kalkan: self.m("kalkan_ad", "HATA", p, "§3.2: kalkan ad; yerine %s" % self.adlar["ajan_adlari_kalkan"][ad])
            elif ad not in kadro: self.m("kadro_disi", "HATA", p, "ADLAR.json'da olmayan ajan")
        for ad in sorted(set(kadro) - set(dosyalar)):
            self.m("ajan_yok", "HATA", os.path.join(self.ajan_dir, ad + ".md"), "21 ajandan biri eksik (§3)")
        toplam = 0
        for ad, p in sorted(dosyalar.items()):
            if ad in kadro: toplam += self.ajan_dosyasi(ad, p, kadro[ad])
        if toplam > AJAN_ACIKLAMA_TOKEN_UYARI: self.m("ajan_aciklama_toplam", "HATA", self.ajan_dir, "açıklamalar ≈ %d token > %d" % (toplam, AJAN_ACIKLAMA_TOKEN_UYARI))
        elif toplam > AJAN_ACIKLAMA_TOKEN_HEDEF: self.m("ajan_aciklama_toplam", "BAYRAK", self.ajan_dir, "açıklamalar ≈ %d token > hedef %d" % (toplam, AJAN_ACIKLAMA_TOKEN_HEDEF))

    def ajan_dosyasi(self, ad, p, kayit):
        metin = oku(p); govde, fm, hata = on_bilgi(metin)
        if fm is None: self.m("frontmatter", "HATA", p, hata); return 0
        if hata: self.m("frontmatter", "HATA", p, hata)
        rol = kayit.get("rol")
        if fm.get("name") != ad: self.m("ajan_adi", "HATA", p, "name (%r) dosya adı değil" % fm.get("name"))
        if str(fm.get("model") or "") not in ("opus", "claude-opus-5-5"): self.m("model", "HATA", p, "model opus olmalı (%r)" % fm.get("model"))
        if fm.get("effort") != "high": self.m("effort", "HATA", p, "effort: high olmalı")
        if fm.get("permissionMode") != "acceptEdits": self.m("izin_kipi", "HATA", p, "permissionMode: acceptEdits olmalı")
        for k in ("memory", "fallbackModel"):
            if k in fm: self.m("yasak_alan", "HATA", p, "%s alanı yazılmaz (§3.1)" % k)
        araclar = arac_listesi(fm.get("tools"))
        if araclar is None: self.m("araclar", "HATA", p, "tools yazılı değil (yoksa bütün araçlar açılır)")
        else:
            izinli = set(ROL_ARACLARI.get(rol, set()))
            if ad in YENI_DOSYA_YAZARLARI: izinli.discard("Edit")
            for a in araclar:
                if YASAK_ARACLAR.match(a): self.m("yasak_arac", "HATA", p, "araç yasak: %s" % a)
                elif a not in izinli: self.m("rol_araci", "HATA", p, "%s rolünde %s yok (§3.1)" % (rol, a))
            if not {"Read", "Write"} <= set(araclar): self.m("araclar", "HATA", p, "Read ve Write şart (yalnız CIKTI'ya yazar)")
            if set(araclar) != izinli and not set(araclar) - izinli:
                self.m("rol_araci", "BAYRAK", p, "rol araç kümesinden eksik: %s" % ", ".join(sorted(izinli - set(araclar))))
        if rol == "kor" and fm.get("omitClaudeMd") is not True: self.m("kor_claude_md", "HATA", p, "kör ajanda omitClaudeMd: true (§3.1)")
        mt = fm.get("maxTurns"); ust = MAX_TURNS.get(ad, MAX_TURNS.get(rol))
        if not isinstance(mt, int): self.m("max_turns", "BAYRAK", p, "maxTurns yazılı değil (tahmin %s)" % ust)
        elif ust and mt > ust: self.m("max_turns", "BAYRAK", p, "maxTurns %d > %d (tahmin)" % (mt, ust))
        acik = str(fm.get("description") or "")
        if not acik: self.m("aciklama", "HATA", p, "description yok")
        elif ACIKLAMA_KALIBI not in acik: self.m("aciklama_kalibi", "BAYRAK", p, "açıklama kalıbı: '%s … çağırdığında kullanılır'" % ACIKLAMA_KALIBI)
        if "KESİN KURAL" not in govde: self.m("govde_kalibi", "BAYRAK", p, "gövdede KESİN KURALLAR bölümü yok (§3.1 kural 4)")
        if "GOREV.json" not in govde: self.m("gorev_protokolu", "HATA", p, "gövde görev defteri protokolünü (GOREV.json) anlatmıyor")
        if "CIKTI" not in govde: self.m("gorev_protokolu", "HATA", p, "gövde yalnız CIKTI'ya yazmayı anlatmıyor")
        if ".md" in govde and "OZET |" not in govde: self.m("ozet_bicimi", "BAYRAK", p, ".md çıktının son satırı 'OZET | …' anlatılmıyor")
        self.soru_tarama(p, govde, ad)
        for n, s in enumerate(govde.split("\n"), 1):
            if rol == "kor" and KOR_SIZINTI.search(s) and not olumsuz(s):
                self.m("kor_sizinti", "BAYRAK", p, "satır %d: kör ajan gövdesi gizli girdiye atıf yapıyor: %r" % (n, s.strip()[:80]))
        sayilar = re.findall(r"(?:≥|≤|en çok|en az)\s*\d+(?:[.,]\d+)?", govde)
        if len(sayilar) > 12: self.m("sabit_sayi", "BAYRAK", p, "gövdede %d sabit eşik; sayılar şablondan gelir (§3.1 kural 6)" % len(sayilar))
        return token_tahmin(acik)

    # -- şablonlar
    def gorev_kumesi(self):
        H = self.H
        if not H: return None
        out = {}
        for a in H.ASAMALAR:
            for g in a.gorevler:
                if g.tur != "ajan": continue
                for k in set(H.kip_listesi(g.kip, 8) if g.kip else [None]): out.setdefault((a.kod, g.ajan, k), set()).add("gorev")
            for b in a.tavan_sonrasi:
                if b.ajan: out.setdefault((a.kod, b.ajan, b.kip), set()).add("merdiven")
        return out

    def sablonlar(self):
        d = os.path.join(self.fy, "sablonlar")
        if not os.path.isdir(d): return
        kadro = self.kadro(); asamalar = set((self.adlar.get("asamalar") or {}).keys())
        gorevler = self.gorev_kumesi()
        var = {}
        for p in sorted(glob.glob(os.path.join(d, "*.md"))):
            ad = os.path.basename(p)[:-3]
            m = re.fullmatch(r"(A\d{2}[a-z]?)_([a-z-]+?)(?:_([a-z0-9_]+))?", ad)
            if not m: self.m("sablon_adi", "HATA", p, "ad kuralı <ASAMA>_<ajan>[_<kip>].md"); continue
            asm, aj, kip = m.group(1), m.group(2), m.group(3)
            if aj not in kadro:
                # tireli ajan adı ile kipin ayrımı: en uzun eşleşen ajan adı
                aday = [k for k in kadro if ad[len(asm) + 1:].startswith(k)]
                if aday:
                    aj = max(aday, key=len); rest = ad[len(asm) + 1 + len(aj):]
                    kip = rest[1:] if rest.startswith("_") else (None if not rest else "?")
            if asm not in asamalar: self.m("sablon_asama", "HATA", p, "bilinmeyen aşama %s" % asm)
            if aj not in kadro: self.m("sablon_ajan", "HATA", p, "kadroda olmayan ajan %s" % aj); continue
            kipler = kadro[aj].get("kipler") or []
            if kip and kip not in kipler: self.m("sablon_kip", "HATA", p, "%s için kip yok: %s" % (aj, kip))
            var[(asm, aj, kip)] = p
            self.sablon_dosyasi(p, aj, kadro[aj].get("rol"))
        if gorevler is not None:
            for anahtar in sorted(set(gorevler) - set(var), key=str):
                asm, aj, kip = anahtar
                self.m("sablon_eksik", "HATA", os.path.join(d, "%s_%s%s.md" % (asm, aj, "_" + kip if kip else "")),
                       "hat/asamalar.py'deki ajan görevinin şablonu yok (%s)" % "/".join(sorted(gorevler[anahtar])))
            for anahtar in sorted(set(var) - set(gorevler), key=str):
                self.m("sablon_kullanilmiyor", "BAYRAK", var[anahtar], "hat/asamalar.py'de bu ajan görevi yok")

    def sablon_dosyasi(self, p, aj, rol):
        t = oku(p); s = t.rstrip("\n").split("\n")
        if len(s) > SABLON_SATIR_MAX: self.m("sablon_satir", "BAYRAK", p, "%d satır > %d" % (len(s), SABLON_SATIR_MAX))
        if not s or not s[0].startswith("# "): self.m("sablon_baslik", "HATA", p, "ilk satır başlık değil")
        for ic in YER_TUTUCU.findall(t):
            if not ic.startswith("esik:"): self.m("sablon_yer_tutucu", "HATA", p, "bilinmeyen yer tutucu {{%s}}" % ic)
            elif self.E and ic[5:].strip() not in self.E: self.m("sablon_esik", "HATA", p, "eşik dosyalarında olmayan anahtar: %s" % ic[5:])
        ozetler = OZET_SATIRI.findall(t)
        for o in ozetler:
            if not OZET_BICIM.match(o.strip()): self.m("ozet_bicimi", "HATA", p, "OZET satırı biçimi: %r" % o[:80])
        cikti = t.split("## CIKTI")[-1].split("## Bitirmeden")[0] if "## CIKTI" in t else ""
        if re.search(r"CIKTI/[\w<>ö-]+\.md", cikti) and not ozetler:
            self.m("ozet_bicimi", "HATA", p, ".md çıktı var ama 'OZET | …' son satırı tanımlı değil (§3.1 kural 5)")
        if aj == "habersiz-seyirci" and ozetler:
            alan = set(re.findall(r"\| ([A-Za-z0-9_]+):", ozetler[0]))
            eksik = (set(OLCUTLER) | {"GENEL", "KRITIK", "ORTA"}) - alan
            if eksik: self.m("ozet_seyirci", "HATA", p, "seyirci OZET satırında eksik alan: %s (§5.8)" % ", ".join(sorted(eksik)))
        for sema in set(re.findall(r"şema `([a-z0-9_]+)`", t)):
            if not os.path.isfile(os.path.join(self.fy, "semalar", sema + ".json")):
                self.m("sablon_sema", "HATA" if sema not in DIS_SEMALAR else "BAYRAK", p, "semalar/%s.json yok" % sema)
        if rol == "kor":
            for n, x in enumerate(s, 1):
                if KOR_SIZINTI.search(x) and not olumsuz(x): self.m("kor_sizinti", "HATA", p, "satır %d: kör şablonda gizli girdi atfı: %r" % (n, x.strip()[:80]))
                if YER_TUTUCU.search(x) and re.search(r"kapı|hedef|esik", x, re.I) and n < 8:
                    self.m("kor_esik", "BAYRAK", p, "kör şablon kapı eşiğini gösteriyor (seyirci etkilenir)")
        self.soru_tarama(p, t, "şablon")

    # -- şemalar
    def semalar(self):
        d = os.path.join(self.fy, "semalar")
        if not os.path.isdir(d): return
        for p in sorted(glob.glob(os.path.join(d, "*.json"))):
            j = json_oku(p)
            if not isinstance(j, dict): self.m("sema_json", "HATA", p, "geçerli JSON değil"); continue
            if "$schema" not in j: self.m("sema_alan", "BAYRAK", p, "$schema yok")
            if j.get("$id") not in (None, os.path.basename(p)[:-5]) and not str(j.get("$id", "")).endswith(os.path.basename(p)[:-5]):
                self.m("sema_alan", "BAYRAK", p, "$id dosya adıyla aynı değil")
            hatalar = sema_ozdenetim(j)
            for h in hatalar[:5]: self.m("sema_yapi", "HATA", p, h)
        for s in ZORUNLU_SEMALAR:
            if not os.path.isfile(os.path.join(d, s + ".json")): self.m("sema_yok", "HATA", os.path.join(d, s + ".json"), "zorunlu şema yok (§4.6)")
        for s in DIS_SEMALAR:
            if not os.path.isfile(os.path.join(d, s + ".json")): self.m("sema_yok", "BAYRAK", os.path.join(d, s + ".json"), "henüz yok (sahibi adım 8)")

    # -- kök CLAUDE.md
    def kok_claude(self):
        p = os.path.join(self.depo, "CLAUDE.md")
        if not os.path.isfile(p): self.m("kok_claude", "HATA", p, "yok"); return
        t = oku(p)
        if TEK_SORU not in t.replace("\n  ", " ").replace("\n", " "):
            self.m("kok_claude", "HATA", p, "tek soru metni yok (§4.7)")
        if BULUT_CUMLESI not in t.replace("\n  ", " ").replace("\n", " "):
            self.m("kok_claude", "HATA", p, "bulut bilgi cümlesi yok (D-45)")
        n = len(t.rstrip("\n").split("\n"))
        if n > 45: self.m("kok_claude_satir", "BAYRAK", p, "%d satır > 45 (§4.7)" % n)

    def kos(self):
        self.beceriler(); self.ajanlar(); self.sablonlar(); self.semalar(); self.kok_claude()
        return sonuc_ozeti(self.maddeler)


def sema_ozdenetim(j, yol="$"):
    """JSON Schema alt kümesinin yapısal denetimi (type/required/properties/items/enum)."""
    h = []
    TIP = {"object", "array", "string", "number", "integer", "boolean", "null"}
    if not isinstance(j, dict): return ["%s: şema nesne değil" % yol]
    t = j.get("type")
    for x in ([t] if isinstance(t, str) else t or []):
        if x not in TIP: h.append("%s: bilinmeyen type %r" % (yol, x))
    if "required" in j:
        if not isinstance(j["required"], list): h.append("%s: required liste değil" % yol)
        elif isinstance(j.get("properties"), dict):
            for r in j["required"]:
                if r not in j["properties"]: h.append("%s: required %r properties'te yok" % (yol, r))
    if "enum" in j and not isinstance(j["enum"], list): h.append("%s: enum liste değil" % yol)
    for k, v in (j.get("properties") or {}).items(): h += sema_ozdenetim(v, "%s.%s" % (yol, k))
    if isinstance(j.get("items"), dict): h += sema_ozdenetim(j["items"], yol + "[]")
    if isinstance(j.get("additionalProperties"), dict): h += sema_ozdenetim(j["additionalProperties"], yol + "{}")
    return h


def sema_dogrula(veri, sema, yol="$"):
    """Küçük doğrulayıcı (type, required, properties, items, enum, const, minimum/maximum, minLength, pattern, additionalProperties,
    minProperties). Testler ve SubagentStop yedeği için; jsonschema kurulu değilse de çalışır."""
    h = []
    TIPLER = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}
    def tip_uyar(v, t):
        if t == "integer": return isinstance(v, int) and not isinstance(v, bool)
        if t == "number": return isinstance(v, (int, float)) and not isinstance(v, bool)
        return isinstance(v, TIPLER[t])
    t = sema.get("type")
    if t is not None:
        ts = [t] if isinstance(t, str) else t
        if not any(tip_uyar(veri, x) for x in ts): return ["%s: tür %s değil" % (yol, "|".join(ts))]
    if "const" in sema and veri != sema["const"]: h.append("%s: %r olmalı" % (yol, sema["const"]))
    if "enum" in sema and veri not in sema["enum"]: h.append("%s: %r izinli değil" % (yol, veri))
    if isinstance(veri, (int, float)) and not isinstance(veri, bool):
        if "minimum" in sema and veri < sema["minimum"]: h.append("%s: %r < %r" % (yol, veri, sema["minimum"]))
        if "maximum" in sema and veri > sema["maximum"]: h.append("%s: %r > %r" % (yol, veri, sema["maximum"]))
    if isinstance(veri, str):
        if "minLength" in sema and len(veri) < sema["minLength"]: h.append("%s: çok kısa" % yol)
        if "pattern" in sema and not re.search(sema["pattern"], veri): h.append("%s: desen %s" % (yol, sema["pattern"]))
    if isinstance(veri, dict):
        for r in sema.get("required") or []:
            if r not in veri: h.append("%s: %s eksik" % (yol, r))
        if "minProperties" in sema and len(veri) < sema["minProperties"]: h.append("%s: boş" % yol)
        pr = sema.get("properties") or {}
        for k, v in veri.items():
            if k in pr: h += sema_dogrula(v, pr[k], "%s.%s" % (yol, k))
            elif sema.get("additionalProperties") is False: h.append("%s: fazladan alan %s" % (yol, k))
            elif isinstance(sema.get("additionalProperties"), dict): h += sema_dogrula(v, sema["additionalProperties"], "%s.%s" % (yol, k))
    if isinstance(veri, list) and isinstance(sema.get("items"), dict):
        for i, v in enumerate(veri): h += sema_dogrula(v, sema["items"], "%s[%d]" % (yol, i))
    return h


def sonuc_ozeti(maddeler):
    oz = {"hata": sum(1 for x in maddeler if x["seviye"] == "HATA"), "bayrak": sum(1 for x in maddeler if x["seviye"] == "BAYRAK")}
    return {"_surum": 1, "_uretim": {"asama": None, "gorev": os.environ.get("YZ_FILM_GOREV"), "girdi_imza": None, "arac_surum": SURUM,
                                     "esik_surum": None, "sonuc": "HATA" if oz["hata"] else ("BAYRAK" if oz["bayrak"] else "GEC"),
                                     "zaman": simdi(), "ortam": "yerel" if os.name == "nt" else "bulut"},
            "sonuc": "HATA" if oz["hata"] else ("BAYRAK" if oz["bayrak"] else "GEC"), "ozet": oz, "maddeler": maddeler}


def denetle(depo=None): return Denetim(depo_bul(depo)).kos()


def hat_yenile(depo=None):
    d = Denetim(depo_bul(depo)); p = os.path.join(d.fy, "reference", "hat.md")
    tab = d.hat_tablosu()
    if tab is None or not os.path.isfile(p): return False
    t = oku(p)
    yeni = re.sub(r"(<!-- hat\.asamalar:bas -->\n).*?(\n<!-- hat\.asamalar:son -->)", lambda m: m.group(1) + "\n".join(tab) + m.group(2), t, flags=re.S)
    if yeni != t: atomik_yaz(p, yeni)
    return True


# ---- §4.8 senaryoları (1–7) ------------------------------------------------------------------------------------------
class Kum:
    """Geçici veri kökü + YOLLAR.json; film.py ve kanca.py gerçek süreçler. Anahtar dosyası yoktur, ağ yoktur."""
    def __init__(self, depo, ortam_="yerel"):
        self.depo = depo; self.kok = tempfile.mkdtemp(prefix="beceri_senaryo_")
        self.veri = os.path.join(self.kok, "VERI")
        sys.path.insert(0, os.path.join(depo, "YZ_FILM", "ARACLAR"))
        import ortak
        y = ortak.varsayilan_yollar(self.veri)
        for k in ("AYARLAR", "FILMLER", "HESAP"): os.makedirs(os.path.join(self.veri, k), exist_ok=True)
        self.filmler = os.path.join(self.veri, "FILMLER")
        y["capcut_taslak"] = os.path.join(self.kok, "CAPCUT_YOK")
        self.yollar = os.path.join(self.kok, "YOLLAR.json")
        atomik_yaz(self.yollar, y); self.y = y
        self.env = dict(os.environ, YZ_FILM_YOLLAR=self.yollar, YZ_FILM_ORTAM=ortam_, CLAUDE_CODE_FORK_SUBAGENT="0",
                        PYTHONIOENCODING="utf-8")
        self.env.pop("YZ_FILM_VERI", None); self.env.pop("YZ_FILM_GOREV", None)
        self.film_py = os.path.join(depo, "YZ_FILM", "ARACLAR", "film.py")
        self.kanca_py = os.path.join(depo, ".claude", "hooks", "kanca.py")
        self.film = None

    def kapat(self): shutil.rmtree(self.kok, ignore_errors=True)

    def f(self, *a, json_=True):
        arg = list(a) + (["--json"] if json_ and a and a[0] not in ("sonraki",) and "--json" not in a else [])
        r = subprocess.run([sys.executable, self.film_py] + arg, capture_output=True, env=self.env, timeout=120)
        out = r.stdout.decode("utf-8", "replace")
        try: j = json.loads(out)
        except ValueError: j = None
        return r.returncode, j, out

    def arac(self, ad, *a):
        r = subprocess.run([sys.executable, os.path.join(self.depo, "YZ_FILM", "ARACLAR", ad)] + list(a), capture_output=True,
                           env=self.env, timeout=120)
        return r.returncode, r.stdout.decode("utf-8", "replace")

    def kanca(self, olay, girdi):
        r = subprocess.run([sys.executable, self.kanca_py, olay], input=json.dumps(girdi).encode("utf-8"), capture_output=True,
                           env=self.env, timeout=60)
        try: j = json.loads(r.stdout.decode("utf-8") or "null")
        except ValueError: j = None
        return r.returncode, j or {}

    def yeni(self, konu="Ejderha yavrusunu saklayan avcı kadın"):
        k, j, _ = self.f("yeni", "--konu", konu, "--saglayici", "sahte")
        if k == 0 and j: self.film = j.get("yol")
        return k, j

    def ajana_kadar(self, sinir=20):
        """sonraki → betikleri çalıştır → ilk ajan grubuna kadar. (kod, json)."""
        for _ in range(sinir):
            k, j, _ = self.f("sonraki")
            if not j or j.get("tur") != "betik": return k, j
            for g in j["gorevler"]: self.f("calis", g["id"])
        return k, j

    def nabiz(self, gid):
        return self.kanca("komut", {"tool_name": "Bash", "tool_input": {"command": "python .claude/bin/film.py basla " + gid},
                                    "cwd": self.depo, "session_id": "beceri_senaryo"})

    def gorev(self, gid): return json_oku(os.path.join(self.film, "_GOREV", gid, "GOREV.json"), {}) or {}

    def iz(self):
        """Film klasörünün içerik izi (salt okunurluk denetimi)."""
        out = {}
        for kok, _, ds in os.walk(self.film):
            for d in ds:
                p = os.path.join(kok, d)
                with open(p, "rb") as f: out[os.path.relpath(p, self.film)] = hashlib.sha1(f.read()).hexdigest()
        return out


def _baglam(j): return ((j or {}).get("hookSpecificOutput") or {}).get("additionalContext") or ""
def _red(k, j): return k == 2 or ((j or {}).get("hookSpecificOutput") or {}).get("permissionDecision") == "deny"


def _s1(K, A):
    k, j = K.kanca("oturum_basi", {"source": "startup", "cwd": K.depo, "session_id": "s"})
    A("oturum başı bağlamı tek soruyu verir", TEK_SORU in _baglam(j), _baglam(j)[:160])
    k, j = K.kanca("istem", {"prompt": "film yap", "cwd": K.depo, "session_id": "s"})
    b = _baglam(j)
    A("çıplak 'film yap' konu sayılmaz; bağlam tek soruyu verir (kanca.py istem)", "Konu verildi" not in b and TEK_SORU in b,
      b[:160] or "(bağlam yok)")
    for m in ("yeni film", "film yapalım"):
        k, j = K.kanca("istem", {"prompt": m, "cwd": K.depo, "session_id": "s"})
        A("'%s' konu sayılmaz" % m, TEK_SORU in _baglam(j) and "Konu verildi" not in _baglam(j), _baglam(j)[:160] or "(bağlam yok)")
    k, j = K.kanca("stop", {"last_assistant_message": TEK_SORU, "cwd": K.depo, "session_id": "s"})
    A("Stop kancası tek soruyu engellemez", (j or {}).get("decision") != "block", json.dumps(j, ensure_ascii=False)[:120])
    sk = oku(os.path.join(K.depo, ".claude", "skills", "film-yap", "SKILL.md"))
    A("film-yap tek soruyu harfiyen ve 'başka cümle eklenmez' kuralıyla taşır", TEK_SORU in sk and "başka cümle eklenmez" in sk, "")
    k, j, out = K.f("ozet")
    A("film.py ozet: aktif film yok", k == 0 and "konu bekleniyor" in ((j or {}).get("ozet") or out), (j or {}).get("ozet") or out[:80])
    A("film açılmadı", not glob.glob(os.path.join(K.filmler, "F*")), "")


def _s2(K, A):
    konu = "Ejderha büyüten bir kadın hakkında film yap"
    k, j = K.kanca("istem", {"prompt": konu, "cwd": K.depo, "session_id": "s"})
    b = _baglam(j)
    A("konu verildi: soru sorulmaz, film-yap ile başlanır", "Konu verildi" in b and TEK_SORU not in b, b[:160])
    k, j = K.yeni(konu)
    A("film.py yeni --konu (sahte) açılır", k == 0 and bool(K.film), json.dumps(j, ensure_ascii=False)[:160])
    if not K.film: return
    k, j = K.ajana_kadar()
    g = (j or {}).get("gorevler") or [{}]
    A("sıradaki iş A01 yapimci·konu ajan görevi", (j or {}).get("tur") == "ajan" and str((j or {}).get("asama", "")).startswith("A01")
      and g[0].get("ajan") == "yapimci" and g[0].get("kip") == "konu", json.dumps(j, ensure_ascii=False)[:200])
    kod, out = K.arac("kredi.py", "but0", "--film", K.film)
    r = json_oku(os.path.join(K.film, "_RAPOR", "BUT0_FILM.json"), {}) or {}
    metin = out + json.dumps(r, ensure_ascii=False)
    A("Ö0-b yokken BUT0 1800 sn seçer ve nedenini yazar", "1800" in metin and "Ö0-b" in metin, out.strip()[:160])


def _s3(K, A):
    K.yeni()
    if not K.film: A("film açıldı", False, ""); return
    k, j = K.ajana_kadar(); gid = ((j or {}).get("gorevler") or [{}])[0].get("id")
    K.nabiz(gid); k, j, _ = K.f("basla", gid)
    A("ajan görevi başladı (nabızla)", k == 0, json.dumps(j, ensure_ascii=False)[:120])
    k, j, _ = K.f("kurtar")                       # oturum kesildi: görev calisiyor kaldı, CIKTI yok
    A("kurtar kesik görevi işaretler", k == 0 and gid in ((j or {}).get("kesildi") or []), json.dumps(j, ensure_ascii=False)[:160])
    k, j = K.kanca("istem", {"prompt": "devam", "cwd": K.depo, "session_id": "s"})
    A("'devam' döngüye yönlendirilir (soru yok)", "sonraki" in _baglam(j) and TEK_SORU not in _baglam(j), _baglam(j)[:140])
    k, j, _ = K.f("sonraki")
    g = ((j or {}).get("gorevler") or [{}])[0]
    A("yalnız kesik iş yeniden gelir (A01 yapimci)", (j or {}).get("tur") == "ajan" and g.get("ajan") == "yapimci", json.dumps(j, ensure_ascii=False)[:160])
    kosu = [json.loads(x).get("gorev") for x in (open(os.path.join(K.film, "_GOREV", "SAHTE_CALISMA.jsonl"), encoding="utf-8").read().splitlines()
            if os.path.exists(os.path.join(K.film, "_GOREV", "SAHTE_CALISMA.jsonl")) else []) if x.strip()]
    A("biten A00 yeniden yapılmadı", kosu.count("A00-HZ-001") <= 1 and K.gorev("A00-HZ-001").get("durum") == "bitti", str(kosu)[:120])


def _s4(K, A):
    K.yeni()
    if not K.film: A("film açıldı", False, ""); return
    k, j = K.ajana_kadar(); gid = ((j or {}).get("gorevler") or [{}])[0].get("id")
    k, j, _ = K.f("basla", gid)                    # kanca nabzı yok (kancalar kapalı)
    A("basla reddeder (kod 1, nabız)", k == 1 and "nabz" in str((j or {}).get("hata", "")).lower(), json.dumps(j, ensure_ascii=False)[:160])
    A("görev hazır kaldı", K.gorev(gid).get("durum") == "hazir", K.gorev(gid).get("durum"))
    A("düz Türkçe yönlendirme KURTARMA.md §Kanca'ya", "KURTARMA.md" in str((j or {}).get("hata", "")), "")
    k2, j2 = K.kanca("ajan", {"tool_name": "Agent", "tool_input": {"subagent_type": "yapimci",
                                                                  "prompt": "Görevin: %s — önce onu oku." % os.path.join(K.film, "_GOREV", gid, "GOREV.json")},
                               "cwd": K.depo, "session_id": "s"})
    A("ajan açılmaz (görev calisiyor değil)", _red(k2, j2), json.dumps(j2, ensure_ascii=False)[:160])


def _s5(K, A):
    K.yeni()
    if not K.film: A("film açıldı", False, ""); return
    k, j = K.ajana_kadar(); gid = ((j or {}).get("gorevler") or [{}])[0].get("id")
    K.nabiz(gid); K.f("basla", gid)
    istem = "Görevin: %s — önce onu oku, yalnız orada yazanı yap." % os.path.join(K.film, "_GOREV", gid, "GOREV.json")
    for tip in ("general-purpose", "Explore", "fork"):
        k2, j2 = K.kanca("ajan", {"tool_name": "Agent", "tool_input": {"subagent_type": tip, "prompt": istem}, "cwd": K.depo, "session_id": "s"})
        A("%s ile seyirci/ajan görevi reddedilir" % tip, _red(k2, j2), json.dumps(j2, ensure_ascii=False)[:120])


def _s6(K, A):
    K.yeni()
    if not K.film: A("film açıldı", False, ""); return
    K.ajana_kadar()
    k, j = K.kanca("istem", {"prompt": "kaç kredi lazım?", "cwd": K.depo, "session_id": "s"})
    A("soru sınıflanır: yalnız cevap (film-durum)", "film-durum" in _baglam(j), _baglam(j)[:140])
    once = K.iz()
    sonuc = [K.f("goster", "maliyet")[0], K.f("ozet", "--uzun")[0], K.f("goster", "neden-durdu")[0], K.f("goster", "token")[0]]
    A("salt okunur komutlar 0 ile döner", all(x == 0 for x in sonuc), str(sonuc))
    A("dosya değişmedi", K.iz() == once, "")
    sk = oku(os.path.join(K.depo, ".claude", "skills", "film-durum", "SKILL.md"))
    _, fm, _ = on_bilgi(sk)
    A("film-durum yazma ve Agent araçlarını kapatır", {"Write", "Edit", "NotebookEdit", "Agent"} <= set(arac_listesi((fm or {}).get("disallowed-tools")) or []), "")


def _s7(K, A):
    K.yeni()
    if not K.film: A("film açıldı", False, ""); return
    k, j, _ = K.f("surus", "kapat", "--gelistirme")
    A("geliştirme kipinde sürüş kapanır", k == 0 and ((j or {}).get("otomatik_surus") or {}).get("acik") is False, json.dumps(j, ensure_ascii=False)[:120])
    k2, j2 = K.kanca("ajan", {"tool_name": "Agent", "tool_input": {"subagent_type": "Explore", "prompt": "kanca.py nerede?"},
                              "cwd": K.depo, "session_id": "s"})
    A("Explore engellenmez", not _red(k2, j2), json.dumps(j2, ensure_ascii=False)[:120])
    k3, j3 = K.kanca("erisim", {"tool_name": "Read", "tool_input": {"file_path": os.path.join(K.depo, "YZ_FILM", "ARACLAR", "film.py")}, "cwd": K.depo})
    A("geliştirmede araç okuma serbest", not _red(k3, j3), json.dumps(j3, ensure_ascii=False)[:120])


SENARYOLAR = {1: ("'film yap' (aktif film yok) → yalnız tek soru", _s1, "yerel"),
              2: ("konu verildi → soru yok, film.py yeni, A01; Ö0-b yoksa BUT0 1800 sn", _s2, "yerel"),
              3: ("'devam' (kesik görev) → yalnız kesik ve kalanlar; bitenler yeniden yapılmaz", _s3, "yerel"),
              4: ("kancalar kapalı 'devam' → basla reddeder, ajan açılmaz", _s4, "yerel"),
              5: ("görev general-purpose ile açılmaya çalışılır → kanca.py ajan reddeder", _s5, "yerel"),
              6: ("'kaç kredi lazım?' → film-durum, dosya değişmez, ajan açılmaz", _s6, "yerel"),
              7: ("geliştirme oturumunda (sürüş kapalı) Explore → engellenmez", _s7, "yerel")}


def senaryolar(nolar=None, depo=None):
    depo = depo_bul(depo); out = []
    for no in (nolar or sorted(SENARYOLAR)):
        ad, f, orm = SENARYOLAR[no]
        adimlar = []
        def A(ne, ok, ayrinti="", seviye="HATA"):
            adimlar.append({"adim": ne, "sonuc": "GEC" if ok else seviye, "ayrinti": ayrinti})
        K = Kum(depo, orm)
        try: f(K, A)
        except Exception as e: adimlar.append({"adim": "senaryo çalıştı", "sonuc": "HATA", "ayrinti": "%s: %s" % (type(e).__name__, e)})
        finally: K.kapat()
        s = "HATA" if any(a["sonuc"] == "HATA" for a in adimlar) else "BAYRAK" if any(a["sonuc"] == "BAYRAK" for a in adimlar) else "GEC"
        out.append({"no": no, "ad": ad, "sonuc": s, "adimlar": adimlar})
    return out


# ---- komut satırı -------------------------------------------------------------------------------------------------
def _arg(a, ad, vars_=None):
    return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else vars_


def main(a=None):
    a = sys.argv[1:] if a is None else list(a)
    if "-h" in a or "--help" in a: print(__doc__); return 0
    depo = depo_bul(_arg(a, "--depo"))
    if not os.path.isdir(os.path.join(depo, ".claude")): print("!! depo bulunamadı: " + depo); return 4
    if "--hat-yenile" in a:
        ok = hat_yenile(depo); print("reference/hat.md " + ("yenilendi" if ok else "yenilenemedi")); return 0 if ok else 4
    if "--sablon" in a:
        ad = _arg(a, "--sablon"); p = ad if os.path.isfile(ad) else os.path.join(depo, ".claude", "skills", "film-yap", "sablonlar", ad)
        if not os.path.isfile(p): print("!! şablon yok: " + ad); return 4
        try: print(sablon_doldur(oku(p), esikleri_yukle(depo, _arg(a, "--ayar"))), end="")
        except SablonHatasi as e: print("!! " + str(e)); return 1
        return 0
    if "--senaryo" in a:
        s = _arg(a, "--senaryo", "hepsi")
        nolar = None if s == "hepsi" else [int(x) for x in s.split(",")]
        r = senaryolar(nolar, depo)
        if "--json" in a: print(json.dumps(r, ensure_ascii=False, indent=1))
        else:
            for x in r:
                print("[%s] %d. %s" % (x["sonuc"], x["no"], x["ad"]))
                for y in x["adimlar"]:
                    if y["sonuc"] != "GEC" or "--uzun" in a: print("    %s · %s %s" % (y["sonuc"], y["adim"], ("— " + y["ayrinti"]) if y["ayrinti"] else ""))
        return 1 if any(x["sonuc"] == "HATA" for x in r) else 0
    r = denetle(depo)
    if _arg(a, "--rapor"): atomik_yaz(_arg(a, "--rapor"), r)
    if "--json" in a: print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        print("BECERİ DENETİM: %s · HATA %d · BAYRAK %d" % (r["sonuc"], r["ozet"]["hata"], r["ozet"]["bayrak"]))
        for x in r["maddeler"]: print("  %-6s %-22s %s — %s" % (x["seviye"], x["madde"], x["dosya"] or "", x["neden"]))
    if r["ozet"]["hata"]: return 1
    return 1 if ("--kati" in a and r["ozet"]["bayrak"]) else 0


if __name__ == "__main__":
    sys.exit(main())
