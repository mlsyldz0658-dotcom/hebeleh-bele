"""AŞAMALAR — A00–A18a aşama kaydı (TASARIM §1.3 tablosunun koddaki tek kaynağı; §1.5 tavan sonrası merdiveni).

Kullanım (kodda):
  from hat.asamalar import ASAMALAR, asama, ana_hat, denetle
  asama("A06").tur_max → 4 · asama("A06").tavan_sonrasi → (Basamak, …)
  denetle() → HATA listesi (boş olmalı; test_asamalar bunu zorlar)
Kullanım (komut satırı; film.py "asamalar --md" de bunu çağırır):
  python -m hat.asamalar [--md | --json]

Alanlar:
  Asama(kod, ad, kim, girdiler[{ad, ureten, dosya}], ciktilar, kapilar, kredi, ortam, tur_max, tavan_sonrasi, geri_don, gorevler, …)
  - girdiler: her girdinin ÜRETENİ zorunludur ([SON] S-3): önceki bir aşamanın kodu ya da DIS_URETICILER'den biri.
    "dosya" verilmişse (film klasörüne göre yol) aşamanın girdi imzasına girer; imza değişirse aşama "bayat" olur ve yeniden açılır.
  - tavan_sonrasi: tur tavanı dolunca açılan merdiven basamakları (§1.5); her aşamada ZORUNLU (boşsa denetle() HATA).
    Basamak.tur: ayni_sahip · ust_sahip (ajan turu + kapı yeniden) · durdu (planlar durdurulur, hat o plansız sürer) ·
                 hedef_alti (hat sürer, FILM_SONU_RAPORU'na) · kagit_urun / kapi6 (6 KAPI; yalnız kapı HATA'sı sürüyorsa).
  - gorevler: GorevSablonu listesi. grup sırası iş sırasıdır; aynı gruptaki ajan görevleri paralel (en çok ajan_paralel_max).
    turda: hepsi | ilk (yalnız tur 1) | sonra (tur ≥ 2 ve merdiven turları). adet: sayı ya da "parti", "sahne_grubu",
    "karakter", "blok", "gorsel_grubu" (film.py dosyalardan çözer).
  - kredi: None ya da "ai84" / "flow" / "flow+ai84" (Flow içerenlerde FLOW_KILIDI varken görev açılmaz: 7 KISIT).
  - ortam: her_ikisi | yerel ; bulutta_test: False ise bulutta (sahte denemede) aşama atlanır.
"""
import json, sys
from dataclasses import dataclass, field

DIS_URETICILER = ("kullanici", "evren", "olcum0", "bakiye", "ders_defteri", "ayar", "kurulum", "youtube")
BASAMAK_TURLERI = ("ayni_sahip", "ust_sahip", "durdu", "hedef_alti", "kagit_urun", "kapi6")
GOREV_TURLERI = ("ajan", "betik", "kullanici")
TURDA = ("hepsi", "ilk", "sonra")
ADET_ANAHTARLARI = ("parti", "sahne_grubu", "karakter", "blok", "gorsel_grubu")
# ADLAR.json'da henüz olmayan, yalnız kâğıt aşamalarında kullanılan kapı kodları (ADLAR'a eklenecek; rapor yolu _RAPOR/<KAPI>_…)
YEREL_KAPILAR = ("HAZIRLIK", "KONU", "BRIFING", "ONERI", "JURI", "YAPI", "HARITA", "PLAN_ELESTIRI", "KUR", "DERS")


@dataclass(frozen=True)
class Girdi:
    ad: str
    ureten: str
    dosya: str = None


@dataclass(frozen=True)
class Kapi:
    kod: str
    rapor: str                      # _RAPOR/... ; {tur} yer tutucusu olabilir
    butce: bool = False             # HATA → 5 BÜTÇE (merdiven yok; yazılmış film kısaltılmaz)
    seyirci: bool = False           # §1.4: KISMI = kapı sağlandı, hedef değil


@dataclass(frozen=True)
class GorevSablonu:
    kod: str                        # görev kimliğinin orta parçası: A06-HS-001
    tur: str                        # ajan | betik | kullanici
    grup: int = 0
    ajan: str = None
    kip: object = None              # str ya da örnek başına tuple
    persona: object = None          # str ya da tuple (habersiz-seyirci A/B/C, mimar ekseni)
    adet: object = 1
    arac: str = None                # betik: ARACLAR altındaki dosya ("film.py:hazirlik" = film.py içi)
    argumanlar: tuple = ()
    cikti: tuple = ()               # betik: film klasörüne göre; ajan: CIKTI/... (zorunlu)
    tasima: tuple = ()              # ajan: (("CIKTI/x.json", "_HIKAYE_ODASI/x_{i}.json"), …)
    girdi: tuple = ()               # ajan: GIRDI'ye kopyalanacak film dosyaları
    kapi: str = None                # bu görevin raporu kapı sonucudur (aşamanın kapilar listesinden)
    kredili: bool = False           # gönderim kaydı önce; kesilince kör yeniden gönderim yok
    asamali: tuple = ()             # aşamalı okuma bölümleri (P0, P1 …)
    mesaj: str = None               # kullanici: aynen iletilecek talimat
    algilama: dict = None           # kullanici: {"tur": "dosya_var", "desen": "GELENLER/*.zip"} | {"tur": "blok", "blok": "KESIT"}
    turda: str = "hepsi"


@dataclass(frozen=True)
class Basamak:
    tur: str
    aciklama: str
    ajan: str = None
    kip: str = None
    butce: str = None               # kuresel_butce anahtarı (h15 …); doluysa basamak atlanır


@dataclass(frozen=True)
class Asama:
    kod: str
    ad: str
    kim: str
    girdiler: tuple
    ciktilar: tuple
    kapilar: tuple
    kredi: str
    ortam: str
    tur_max: int
    tavan_sonrasi: tuple
    geri_don: str
    gorevler: tuple
    bulutta_test: bool = True
    istege_bagli: bool = False
    butce: str = None               # tur sayısının düştüğü küresel bütçe (animatik_kurgu_tur)
    kosul: str = None               # istege_bagli aşamanın açılma koşulu (bilgi)
    gorev_tahmin: int = None        # olcek.py yoksa görev tavanı tahmini (yoksa şablonlardan hesaplanır)


# --- kısa kurucular ------------------------------------------------------------------------------------------------------
def B(kod, arac, *args, grup=0, cikti=(), kapi=None, kredili=False, turda="hepsi"):
    return GorevSablonu(kod=kod, tur="betik", grup=grup, arac=arac, argumanlar=tuple(args), cikti=tuple(cikti), kapi=kapi,
                        kredili=kredili, turda=turda)


def J(kod, ajan, kip=None, *, grup=0, adet=1, persona=None, cikti=("CIKTI/rapor.json",), tasima=(), girdi=(), asamali=(),
      kapi=None, turda="hepsi"):
    return GorevSablonu(kod=kod, tur="ajan", grup=grup, ajan=ajan, kip=kip, persona=persona, adet=adet, cikti=tuple(cikti),
                        tasima=tuple(tasima), girdi=tuple(girdi), asamali=tuple(asamali), kapi=kapi, turda=turda)


def K(kod, mesaj, algilama, grup=0, turda="hepsi"):
    return GorevSablonu(kod=kod, tur="kullanici", grup=grup, mesaj=mesaj, algilama=algilama, turda=turda)


def G(ad, ureten, dosya=None): return Girdi(ad, ureten, dosya)


def M(tur, aciklama, ajan=None, kip=None, butce=None): return Basamak(tur, aciklama, ajan, kip, butce)


def R(kod, rapor, **k): return Kapi(kod, rapor, **k)


SEYIRCI = ("A", "B", "C")
BOLUMLER = ("P0", "P1", "P2", "P3")
DURDU_SIFIR = M("durdu", "plan ya da sahne durdu: kurgucu·sifir_kredi zorunlu çözümü yazar; BAYRAK; hat o plansız sürer (§1.5 basamak 3)",
                "kurgucu", "sifir_kredi")
KOD_HATASI = M("kapi6", "araç ya da şema HATA'sı (kod hatası): hat durur, film-gelistir işi olur; kullanıcıya bilgi (§1.5 basamak 4)")
DAR = M("ust_sahip", "üst sahip: sahneyi sadeleştir, böl ya da kes (H15 bütçesinden)", "hikaye-yazari", "dar_degisiklik", butce="h15")
DOKTOR = M("ust_sahip", "film düzeyi: yapimci·doktor yapısal tur", "yapimci", "doktor")
HEDEF_ALTI = M("hedef_alti", "kalan maddeler hedef_alti ve açık eksik raporuyla (FILM_SONU_RAPORU.md) sürer (§1.5 basamak 5)")


def _seyirci_turu(kip, kapi, rapor_kok, grup0, seyirci_kip=None):
    """Kör paket → habersiz seyirci ×3 (aşamalı) + ilk 2 dk ×3 → özet eşleştirici ×3 → seyirci_topla (kapı)."""
    return (
        B("KP", "kor_paket.py", "--kip", kip, grup=grup0),
        J("HS", "habersiz-seyirci", seyirci_kip or kip, grup=grup0 + 1, adet=3, persona=SEYIRCI, asamali=BOLUMLER,
          cikti=("CIKTI/rapor.json",), tasima=(("CIKTI/rapor.json", "_RAPOR/SEYIRCI/%s_t{tur}/s{i}_rapor.json" % kip),)),
        J("IK", "habersiz-seyirci", "ilk2dk", grup=grup0 + 1, adet=3, persona=SEYIRCI,
          tasima=(("CIKTI/rapor.json", "_RAPOR/SEYIRCI/%s_ilk2dk_t{tur}/s{i}_rapor.json" % kip),)),
        J("OE", "ozet-eslestirici", "ozet", grup=grup0 + 2, adet=3,
          tasima=(("CIKTI/rapor.json", "_RAPOR/SEYIRCI/%s_t{tur}/e{i}_eslesme.json" % kip),)),
        B("ST", "seyirci_topla.py", "--kip", kip, "--tur", "{tur}", grup=grup0 + 3, cikti=(rapor_kok,), kapi=kapi),
    )


ASAMALAR = (
    Asama("A00", "Hazırlık ve konu", "betik film.py yeni + hazirlik; ana Claude yalnız tek soruyu sorar (bulutta sormaz, D-45)",
          (G("kullanıcının cümlesi", "kullanici", "00_KONU.md"),),
          ("00_KONU.md", "HAZIRLIK.json"), (R("HAZIRLIK", "_RAPOR/HAZIRLIK_t{tur}.json"),), None, "her_ikisi", 1,
          (KOD_HATASI,), None,
          (B("HZ", "film.py:hazirlik", cikti=("HAZIRLIK.json", "_RAPOR/HAZIRLIK_t{tur}.json"), kapi="HAZIRLIK"),)),
    Asama("A01", "Konu kartı ve süre (BUT0)", "yapimci·konu; betik hikaye_odasi.py konu-denetim, kredi.py but0",
          (G("00_KONU.md", "A00", "00_KONU.md"), G("evren özeti", "evren"), G("OLCUM0.json", "olcum0"), G("bakiye", "bakiye")),
          ("_HIKAYE_ODASI/01_KONU_KARTI.json", "_HIKAYE_ODASI/01_VARSAYIMLAR.md", "KARAR_DEFTERI.md", "_RAPOR/BUT0_FILM.json"),
          (R("KONU", "_RAPOR/KONU_t{tur}.json"), R("BUT0", "_RAPOR/BUT0_FILM.json", butce=True)), None, "her_ikisi", 1,
          (M("ayni_sahip", "yapimci·konu yeni eksenle 1 kez (ör. çocuk kahraman → yetişkin)", "yapimci", "konu"),
           M("kapi6", "konu bu sistemle üretilemez: yüzüne vur raporu, kâğıt ürün yok, 6 KAPI (§1.5 A01)")), None,
          (J("YK", "yapimci", "konu", grup=0, girdi=("00_KONU.md",),
             cikti=("CIKTI/01_KONU_KARTI.json", "CIKTI/01_VARSAYIMLAR.md"),
             tasima=(("CIKTI/01_KONU_KARTI.json", "_HIKAYE_ODASI/01_KONU_KARTI.json"),
                     ("CIKTI/01_VARSAYIMLAR.md", "_HIKAYE_ODASI/01_VARSAYIMLAR.md"))),
           B("KD", "hikaye_odasi.py", "konu-denetim", grup=1, cikti=("_RAPOR/KONU_t{tur}.json",), kapi="KONU"),
           B("B0", "kredi.py", "but0", grup=1, cikti=("_RAPOR/BUT0_FILM.json",), kapi="BUT0"))),
    Asama("A02", "Brifing", "betik hikaye_odasi.py brifing",
          (G("konu kartı", "A01", "_HIKAYE_ODASI/01_KONU_KARTI.json"), G("aktif hikâye dersleri", "ders_defteri"),
           G("ritim eşikleri", "ayar")),
          ("_HIKAYE_ODASI/00_BRIFING.md",), (R("BRIFING", "_RAPOR/BRIFING_t{tur}.json"),), None, "her_ikisi", 1,
          (KOD_HATASI,), None,
          (B("BR", "hikaye_odasi.py", "brifing", cikti=("_HIKAYE_ODASI/00_BRIFING.md", "_RAPOR/BRIFING_t{tur}.json"),
             kapi="BRIFING"),)),
    Asama("A03", "Dört öneri", "hikaye-mimari ×3 (D/S/E, paralel) + 1 (X); betik oneri-denetim",
          (G("brifing", "A02", "_HIKAYE_ODASI/00_BRIFING.md"),),
          ("_HIKAYE_ODASI/02_oneri_<eksen>.md",), (R("ONERI", "_RAPOR/ONERI_t{tur}.json"),), None, "her_ikisi", 1,
          (M("ayni_sahip", "BENZER: yeni eksenle 1 kez", "hikaye-mimari"),
           M("hedef_alti", "yine BENZER: en ayrışan dört öneriyle jüriye gidilir, çeşitlilik BAYRAK'ı jüri paketine")), None,
          (J("HM", "hikaye-mimari", grup=0, adet=3, persona=("D", "S", "E"), girdi=("_HIKAYE_ODASI/00_BRIFING.md",),
             cikti=("CIKTI/oneri.md",), tasima=(("CIKTI/oneri.md", "_HIKAYE_ODASI/02_oneri_{persona}.md"),)),
           J("HX", "hikaye-mimari", grup=1, persona="X", girdi=("_HIKAYE_ODASI/00_BRIFING.md",),
             cikti=("CIKTI/oneri.md",), tasima=(("CIKTI/oneri.md", "_HIKAYE_ODASI/02_oneri_X.md"),)),
           B("OD", "hikaye_odasi.py", "oneri-denetim", grup=2, cikti=("_RAPOR/ONERI_t{tur}.json",), kapi="ONERI"))),
    Asama("A04", "Kör jüri ve seçim", "juri-uyesi × 4 rol + uretilebilirlik-denetcisi·juri; betik juri-topla",
          (G("anonim öneriler", "A03", "_HIKAYE_ODASI/02_oneri_D.md"),),
          ("_HIKAYE_ODASI/04_SECIM.json", "_HIKAYE_ODASI/04_KULLANICIYA_OZET.md"), (R("JURI", "_RAPOR/JURI_t{tur}.json"),),
          None, "her_ikisi", 1,
          (M("ayni_sahip", "kazanan < 8,0 ya da veto: yazar 1 kez yeniden + jüri", "hikaye-mimari"),
           M("hedef_alti", "veto almamış en yüksek medyanlı öneri kazanır (hedef_alti)")), None,
          (B("JP", "hikaye_odasi.py", "juri-paketi", grup=0),
           J("JU", "juri-uyesi", ("ilk_kez_izleyen", "youtube_stratejisti", "tur_uzmani", "duygu_elestirmeni"), grup=1, adet=4,
             tasima=(("CIKTI/rapor.json", "_HIKAYE_ODASI/03_juri_{kip}.json"),)),
           J("UJ", "uretilebilirlik-denetcisi", "juri", grup=1,
             tasima=(("CIKTI/rapor.json", "_HIKAYE_ODASI/03_juri_uretilebilirlik.json"),)),
           B("JT", "hikaye_odasi.py", "juri-topla", grup=2, cikti=("_HIKAYE_ODASI/04_SECIM.json", "_RAPOR/JURI_t{tur}.json"),
             kapi="JURI"))),
    Asama("A05", "Yapı ve senaryo", "hikaye-yazari·yapi, ·senaryo; oyuncu × ana karakter; diyalog-editoru; yapi-denetim, senaryo-denetim",
          (G("04_SECIM.json", "A04", "_HIKAYE_ODASI/04_SECIM.json"), G("kazanan öneri", "A03")),
          ("_HIKAYE_ODASI/05_YAPI.json", "_HIKAYE_ODASI/06_SENARYO_v<N>.json", "_RAPOR/HIKAYE_Z_v<N>.json"),
          (R("YAPI", "_RAPOR/YAPI_t{tur}.json"), R("SEMA", "_RAPOR/HIKAYE_Z_v{tur}.json")), None, "her_ikisi", 3,
          (DOKTOR, M("ust_sahip", "dar değişiklik: filtre, NE YOK ve şema maddeleri silinerek kapanır", "hikaye-yazari",
                     "dar_degisiklik"),
           M("hedef_alti", "Z1/Z2 hikâye ölçüleri hedef_alti ile sürer (§1.5 A05)")), None,
          (J("HY", "hikaye-yazari", "yapi", grup=0, girdi=("_HIKAYE_ODASI/04_SECIM.json",), turda="ilk",
             cikti=("CIKTI/05_YAPI.json",), tasima=(("CIKTI/05_YAPI.json", "_HIKAYE_ODASI/05_YAPI.json"),)),
           J("RV", "hikaye-yazari", "revizyon", grup=0, turda="sonra", girdi=("_HIKAYE_ODASI/05_YAPI.json",),
             cikti=("CIKTI/05_YAPI.json",), tasima=(("CIKTI/05_YAPI.json", "_HIKAYE_ODASI/05_YAPI.json"),)),
           B("YD", "hikaye_odasi.py", "yapi-denetim", grup=1, cikti=("_RAPOR/YAPI_t{tur}.json",), kapi="YAPI"),
           J("SN", "hikaye-yazari", "senaryo", grup=2, girdi=("_HIKAYE_ODASI/05_YAPI.json",),
             cikti=("CIKTI/senaryo.json",), tasima=(("CIKTI/senaryo.json", "_HIKAYE_ODASI/06_SENARYO_v{tur}.json"),)),
           J("OY", "oyuncu", grup=3, adet="karakter", tasima=(("CIKTI/rapor.json", "_HIKAYE_ODASI/oyuncu/{i}.json"),)),
           J("DE", "diyalog-editoru", grup=4, tasima=(("CIKTI/rapor.json", "_HIKAYE_ODASI/diyalog_t{tur}.json"),)),
           B("SD", "hikaye_odasi.py", "senaryo-denetim", grup=5, cikti=("_RAPOR/HIKAYE_Z_v{tur}.json",), kapi="SEMA"))),
    Asama("A06", "Kâğıt seyirci, ilk 2 dk, kilit", "habersiz-seyirci·kagit ×3 (aşamalı), ·ilk2dk ×3, ozet-eslestirici ×3; seyirci_topla; devir",
          (G("senaryo EKRAN bloğu", "A05", "_HIKAYE_ODASI/06_SENARYO_v1.json"),),
          ("_RAPOR/HS_KAGIT_FILM_t<n>.json", "HIKAYE.json", "HIKAYE.md"),
          (R("HS_KAGIT", "_RAPOR/HS_KAGIT_FILM_t{tur}.json", seyirci=True),), None, "her_ikisi", 4,
          (DOKTOR, DOKTOR,
           M("ayni_sahip", "konu kartı bir kez yeniden yorumlanır (yeni eksen) ve ikinci öneriyle tur", "yapimci", "konu"),
           M("kagit_urun", "kapı sağlanmıyor: kâğıt ürün (senaryo) yüzüne vur raporuyla teslim, videoya geçilmez (§1.4)")), None,
          (J("RV", "hikaye-yazari", "revizyon", grup=0, turda="sonra",
             tasima=(("CIKTI/rapor.json", "_HIKAYE_ODASI/DEGISIKLIK_v{tur}.json"),)),)
          + _seyirci_turu("kagit", "HS_KAGIT", "_RAPOR/HS_KAGIT_FILM_t{tur}.json", 1)
          + (B("DV", "hikaye_odasi.py", "devir", grup=5, cikti=("HIKAYE.json", "HIKAYE.md")),)),
    Asama("A06s", "Ses kadrosu (kâğıt)", "ses-tasarimcisi·kadro; betik ses_plani.py --profil-denetle",
          (G("HIKAYE.json", "A06", "HIKAYE.json"), G("evren ses kayıtları", "evren")),
          ("_SES/SES_PROFILLERI.json", "_SES/SES_KADROSU.md"), (R("S0", "_RAPOR/S0_PROFIL_t{tur}.json"),), None, "her_ikisi", 1,
          (M("hedef_alti", "kural ihlali kodla kırpılır ve BAYRAK; aksan bilinmiyorsa neutral + BAYRAK"),), None,
          (J("SK", "ses-tasarimcisi", "kadro", grup=0, girdi=("HIKAYE.json",), cikti=("CIKTI/SES_PROFILLERI.json",),
             tasima=(("CIKTI/SES_PROFILLERI.json", "_SES/SES_PROFILLERI.json"),)),
           B("PD", "ses_plani.py", "--profil-denetle", grup=1, cikti=("_RAPOR/S0_PROFIL_t{tur}.json",), kapi="S0"))),
    Asama("A07a", "Harita, kroki, kart tarifleri", "yonetmen·harita × parti ∥ kart-tasarimcisi; kroki.py --karsilikli/--ciz",
          (G("HIKAYE.json", "A06", "HIKAYE.json"), G("evren mekânları", "evren")),
          ("_YONETMEN/HARITA_P<n>.json", "_YONETMEN/KART_ISTEGI.json", "_KARTLAR/KART_SPEC.json"),
          (R("HARITA", "_RAPOR/HARITA_t{tur}.json"),), None, "her_ikisi", 1,
          (M("ayni_sahip", "harita: yonetmen·harita yeni örnek 1 kez", "yonetmen", "harita"), DAR, DURDU_SIFIR), None,
          (B("KR", "kroki.py", "--karsilikli", grup=0),
           J("YH", "yonetmen", "harita", grup=1, adet="parti", girdi=("HIKAYE.json",), cikti=("CIKTI/HARITA.json",),
             tasima=(("CIKTI/HARITA.json", "_YONETMEN/HARITA_P{i}.json"),)),
           J("KT", "kart-tasarimcisi", grup=1, girdi=("HIKAYE.json",), cikti=("CIKTI/KART_SPEC.json",),
             tasima=(("CIKTI/KART_SPEC.json", "_KARTLAR/KART_SPEC.json"),)),
           B("PH", "plan_denetim.py", "--harita", grup=2, cikti=("_RAPOR/HARITA_t{tur}.json",), kapi="HARITA"),
           B("KC", "kroki.py", "--ciz", grup=3))),
    Asama("A07b", "Sahne grubu planları", "yonetmen·plan × sahne grubu (paralel ≤ 5); betik dilim.py, plan_denetim --sahne",
          (G("haritalar", "A07a", "_YONETMEN/HARITA_P1.json"), G("HIKAYE.json", "A06", "HIKAYE.json"),
           G("kroki PNG", "A07a"), G("dersler", "ders_defteri")),
          ("_YONETMEN/PLANLAR/S<k>.json",), (R("Z0", "_RAPOR/Z0_SAHNE_t{tur}.json"),), None, "her_ikisi", 1,
          (M("ayni_sahip", "partinin harita revizyonu 1 kez", "yonetmen", "harita"), DURDU_SIFIR), None,
          (B("DL", "dilim.py", "--asama", "A07b", grup=0),
           J("YP", "yonetmen", "plan", grup=1, adet="sahne_grubu", cikti=("CIKTI/plan.json",),
             tasima=(("CIKTI/plan.json", "_YONETMEN/PLANLAR/G{i}.json"),)),
           B("PS", "plan_denetim.py", "--sahne", "--tum", grup=2, cikti=("_RAPOR/Z0_SAHNE_t{tur}.json",), kapi="Z0"))),
    Asama("A07c", "Birleştirme, K0, T0, BUT1", "betik plan_birlestir, dunya_defteri, zaman_cizelgesi, kredi.py but1, olcek.py, cekim_listesi",
          (G("planlar", "A07b", "_YONETMEN/PLANLAR"), G("evren karakter kayıtları", "evren")),
          ("SAHNELER.json", "DUNYA_DEFTERI.json", "_RAPOR/K0_FILM.json", "KURGU/surumler/KURGU_PLANI_T0.json",
           "URETIM_ONIZLEME.json"),
          (R("K0", "_RAPOR/K0_FILM.json"), R("BUT1", "_RAPOR/BUT1_FILM.json", butce=True)), None, "her_ikisi", 3,
          (DURDU_SIFIR,), "A07b",
          (J("YO", "yonetmen", "onarim", grup=0, turda="sonra", tasima=(("CIKTI/rapor.json", "_YONETMEN/ONARIM_t{tur}.json"),)),
           B("PB", "plan_birlestir.py", grup=1, cikti=("SAHNELER.json",)),
           B("DD", "dunya_defteri.py", "--derle", "--denetle", grup=2, cikti=("DUNYA_DEFTERI.json", "_RAPOR/K0_FILM.json"),
             kapi="K0"),
           B("ZC", "zaman_cizelgesi.py", "--asama", "kagit", grup=3, cikti=("KURGU/surumler/KURGU_PLANI_T0.json",)),
           B("B1", "kredi.py", "but1", grup=4, cikti=("_RAPOR/BUT1_FILM.json", "URETIM_ONIZLEME.json"), kapi="BUT1"),
           B("CL", "cekim_listesi.py", grup=5))),
    Asama("A07d", "Kâğıt plan eleştirisi", "plan-elestirmeni ×3 ∥ uretilebilirlik-denetcisi·plan ×3 ∥ sureklilik-denetcisi·kagit ×3",
          (G("çekim listeleri", "A07c"), G("K0 BAYRAK'ları", "A07c", "_RAPOR/K0_FILM.json")),
          ("_RAPOR/PLAN_ELESTIRI_P<n>_t<n>.json",), (R("PLAN_ELESTIRI", "_RAPOR/PLAN_ELESTIRI_FILM_t{tur}.json"),),
          None, "her_ikisi", 2,
          (M("ayni_sahip", "kalan KRİTİK → yonetmen·onarim 1 kez", "yonetmen", "onarim"), DAR, DURDU_SIFIR), None,
          (J("YO", "yonetmen", "onarim", grup=0, turda="sonra", tasima=(("CIKTI/rapor.json", "_YONETMEN/ONARIM_d{tur}.json"),)),
           J("PE", "plan-elestirmeni", grup=1, adet=3, tasima=(("CIKTI/rapor.json", "_RAPOR/PLAN_ELESTIRI/pe_t{tur}_{i}.json"),)),
           J("UP", "uretilebilirlik-denetcisi", "plan", grup=1, adet=3,
             tasima=(("CIKTI/rapor.json", "_RAPOR/PLAN_ELESTIRI/up_t{tur}_{i}.json"),)),
           J("SU", "sureklilik-denetcisi", "kagit", grup=1, adet=3,
             tasima=(("CIKTI/rapor.json", "_RAPOR/PLAN_ELESTIRI/su_t{tur}_{i}.json"),)),
           B("PO", "puan_oku.py", "--plan", "--tur", "{tur}", grup=2, cikti=("_RAPOR/PLAN_ELESTIRI_FILM_t{tur}.json",),
             kapi="PLAN_ELESTIRI"))),
    Asama("A07e", "Plan seyircisi", "habersiz-seyirci·plan ×3/parti; ozet-eslestirici; seyirci_topla",
          (G("SAHNELER.json", "A07c", "SAHNELER.json"),), ("_RAPOR/HS_PLAN_P<n>_t<n>.json",),
          (R("HS_PLAN", "_RAPOR/HS_PLAN_FILM_t{tur}.json", seyirci=True),), None, "her_ikisi", 2,
          (DOKTOR, M("kagit_urun", "kapı sağlanmıyor: kâğıt ürün teslim, videoya geçilmez (§1.4)")), None,
          _seyirci_turu("plan", "HS_PLAN", "_RAPOR/HS_PLAN_FILM_t{tur}.json", 0)),
    Asama("A08", "Ses tasarımı ve müzik planı", "ses_plani --taslak; ses-tasarimcisi·tasarim × sahne grubu, ·muzik; muzik.py --kagit; S0",
          (G("SAHNELER.json", "A07c", "SAHNELER.json"), G("DUNYA_DEFTERI.json", "A07c", "DUNYA_DEFTERI.json"),
           G("evren müzik", "evren")),
          ("_SES/SES_<S>.json", "_SES/SES_TASARIMI.md", "MUZIK/muzik_listesi.json", "_RAPOR/S0_FILM.json"),
          (R("S0", "_RAPOR/S0_FILM.json"),), None, "her_ikisi", 1,
          (M("ayni_sahip", "S0 maddesi: ses-tasarimcisi·tasarim yeni örnek 1 kez", "ses-tasarimcisi", "tasarim"),
           M("hedef_alti", "kod varsayılanı (tek yatak, efektsiz) + BAYRAK")), None,
          (B("ST", "ses_plani.py", "--taslak", grup=0),
           J("SE", "ses-tasarimcisi", "tasarim", grup=1, adet="sahne_grubu", cikti=("CIKTI/SES.json",),
             tasima=(("CIKTI/SES.json", "_SES/SES_G{i}.json"),)),
           J("SM", "ses-tasarimcisi", "muzik", grup=1, cikti=("CIKTI/muzik_listesi.json",),
             tasima=(("CIKTI/muzik_listesi.json", "MUZIK/muzik_listesi.json"),)),
           B("MK", "muzik.py", "--kagit", grup=2),
           B("SD", "ses_plani.py", "--denetle", "--tum", grup=3, cikti=("_RAPOR/S0_FILM.json",), kapi="S0"))),
    Asama("A09", "İstem derleme ve kâğıt sonu", "betik istem_derle --hareket, istem_denetim, kamera_agaci",
          (G("SAHNELER.json (zanaat + ses)", "A07c", "SAHNELER.json"), G("ses tasarımı", "A08", "_RAPOR/S0_FILM.json")),
          ("SAHNELER.json", "KAMERA_AGACI.json", "_RAPOR/ISTEM_FILM.json", "KAGIT_TAMAM.json"),
          (R("ISTEM", "_RAPOR/ISTEM_FILM.json"),), None, "her_ikisi", 3, (DURDU_SIFIR,), None,
          (J("YO", "yonetmen", "onarim", grup=0, turda="sonra", tasima=(("CIKTI/rapor.json", "_YONETMEN/ONARIM_i{tur}.json"),)),
           B("ID", "istem_derle.py", "--hareket", grup=1, cikti=("SAHNELER.json",)),
           B("DN", "istem_denetim.py", "--film", grup=2, cikti=("_RAPOR/ISTEM_FILM.json",), kapi="ISTEM"),
           B("KA", "kamera_agaci.py", grup=3, cikti=("KAMERA_AGACI.json", "KAGIT_TAMAM.json")))),
    Asama("A10a", "Yerel kurulum ölçümü", "betik kurulum.py --dogrula, olcum/ses.py --kontrol",
          (G("kurulum", "kurulum"),), ("_RAPOR/KURULUM_FILM.json",), (R("KUR", "_RAPOR/KURULUM_FILM.json"),), None, "yerel", 1,
          (M("hedef_alti", "eksik KUR2/KUR3 ortamı yalnız kendi basamağını kapatır"),), None,
          (B("KD", "kurulum.py", "--dogrula", "--film", cikti=("_RAPOR/KURULUM_FILM.json",), kapi="KUR"),),
          bulutta_test=False),
    Asama("A10b", "Telaffuz testi", "betik ses_sec.py --telaffuz (yerelin ilk işi)",
          (G("uydurma adlar", "A06", "HIKAYE.json"),), ("_RAPOR/S1a_telaffuz.json",), (R("S1a", "_RAPOR/S1a_telaffuz.json"),),
          "ai84", "yerel", 1,
          (M("ust_sahip", "geçmeyen ad: hikaye-yazari·dar_degisiklik (H15)", "hikaye-yazari", "dar_degisiklik", butce="h15"),
           M("hedef_alti", "ad yalnız yazıyla (altyazı ve kart), replikte hitap kullanılmaz + BAYRAK")), None,
          (B("TL", "ses_sec.py", "--telaffuz", cikti=("_RAPOR/S1a_telaffuz.json",), kapi="S1a", kredili=True),)),
    Asama("A10c", "Ses seçimi, motor kıyası, efekt", "betik ses_sec.py --ara/--olc/--sec; yakın puanda ses-tasarimcisi·kadro",
          (G("ses profilleri", "A06s", "_SES/SES_PROFILLERI.json"),), ("_RAPOR/S1_FILM.json",), (R("S1", "_RAPOR/S1_FILM.json"),),
          "ai84", "yerel", 1,
          (M("ayni_sahip", "puan farkı < 0,03: ses-tasarimcisi·kadro", "ses-tasarimcisi", "kadro"),
           M("hedef_alti", "ölçü sırasıyla en iyi aday + BAYRAK + izle-dinle örneği")), None,
          (B("SS", "ses_sec.py", "--ara", "--olc", "--sec", cikti=("_RAPOR/S1_FILM.json",), kapi="S1", kredili=True),)),
    Asama("A10d", "Kartlar", "istem_derle --kart → gemini_paket (kullanıcı taşır) → gemini_al; kart_denetim + kare-tarifcisi·kart; yonetmen·kart_secimi",
          (G("KART_SPEC.json", "A07a", "_KARTLAR/KART_SPEC.json"),), ("_RAPOR/KART_KAPISI.json", "_KARTLAR/KART_SECIM.json"),
          (R("KART", "_RAPOR/KART_KAPISI.json"),), None, "yerel", 2,
          (M("ayni_sahip", "kart tarifi revizyonu", "kart-tasarimcisi", butce="kart_tarif"),
           M("hedef_alti", "yonetmen·kart_secimi en iyi teknik adayı seçer, BAYRAK", "yonetmen", "kart_secimi")), None,
          (B("IK", "istem_derle.py", "--kart", grup=0),
           B("GP", "gemini_paket.py", "--kartlar", grup=1),
           K("GZ", "Masaüstündeki GEMINI GORSEL ISTEM klasöründeki kart paketini Gemini'ye ver; gelen ZIP'i filmin GELENLER "
                   "klasörüne koy. Ben ZIP'i görünce kendim devam ederim.",
             {"tur": "dosya_var", "desen": "GELENLER/*KART*.zip"}, grup=2),
           B("GA", "gemini_al.py", "--kartlar", grup=3),
           J("KF", "kare-tarifcisi", "kart", grup=4, tasima=(("CIKTI/rapor.json", "_KARTLAR/gozlem_t{tur}_{i}.json"),)),
           B("KD", "kart_denetim.py", grup=5, cikti=("_RAPOR/KART_KAPISI.json",), kapi="KART"),
           J("KS", "yonetmen", "kart_secimi", grup=6, cikti=("CIKTI/KART_SECIM.json",),
             tasima=(("CIKTI/KART_SECIM.json", "_KARTLAR/KART_SECIM.json"),)),
           B("EK", "evren.py", "--kilitle", grup=7))),
    Asama("A11", "Başlangıç görselleri, G1 ilk geçiş, kapak adayları", "istem_derle --gorsel, gemini_paket → gemini_al; kare-tarifcisi·g1; kare_denetim --karar; kapak",
          (G("SAHNELER.json", "A09", "KAGIT_TAMAM.json"), G("kilitli kartlar", "A10d", "_KARTLAR/KART_SECIM.json")),
          ("SIRALI_GORSEL/NNN.jpg", "_RAPOR/G1_P<n>_B<k>.json", "KUYRUK/YENIDEN_URET.json", "YAYIN/KAPAK_SPEC.json"),
          (R("G1", "_RAPOR/G1_FILM_t{tur}.json"), R("HS_KAPAK", "_RAPOR/KAPAK_t{tur}.json", seyirci=True)), None, "yerel", 2,
          (M("hedef_alti", "yer tutucu > %15: animatik tur 1 yer tutucularla koşar (D-14); kimlik maddeleri G1 merdivenine"),), None,
          (B("IG", "istem_derle.py", "--gorsel", grup=0),
           B("GP", "gemini_paket.py", "--basamak", "1", "--aday", "2", grup=1),
           K("GZ", "Masaüstündeki GEMINI GORSEL ISTEM klasöründeki görsel paketini Gemini'ye ver; gelen ZIP'i filmin GELENLER "
                   "klasörüne koy. Ben ZIP'i görünce kendim devam ederim.",
             {"tur": "dosya_var", "desen": "GELENLER/*GORSEL*.zip"}, grup=2),
           B("GA", "gemini_al.py", grup=3),
           B("OL", "kare_denetim.py", "--olc", grup=4),
           J("KG", "kare-tarifcisi", "g1", grup=5, adet="gorsel_grubu",
             tasima=(("CIKTI/rapor.json", "_RAPOR/G1/gozlem_t{tur}_{i}.json"),)),
           B("KK", "kare_denetim.py", "--karar", grup=6, cikti=("_RAPOR/G1_FILM_t{tur}.json",), kapi="G1"),
           J("KP", "kare-tarifcisi", "kapak", grup=7, tasima=(("CIKTI/rapor.json", "_RAPOR/KAPAK/gozlem_t{tur}.json"),)),
           J("HK", "habersiz-seyirci", "kapak", grup=7, tasima=(("CIKTI/rapor.json", "_RAPOR/KAPAK/seyirci_t{tur}.json"),)),
           B("KS", "kapak.py", "--sec", grup=8, cikti=("_RAPOR/KAPAK_t{tur}.json",), kapi="HS_KAPAK"))),
    Asama("A12", "Animatik", "zaman_cizelgesi T1, seslendir --animatik, muzik, ses_katmani, son_miks, kurgu_render; habersiz-seyirci·animatik ×3",
          (G("görseller", "A11", "_RAPOR/G1_FILM_t1.json"), G("sesler", "A10c", "_RAPOR/S1_FILM.json"),
           G("HIKAYE.json", "A06", "HIKAYE.json")),
          ("ANIMATIK/animatik_v<N>.mp4", "_RAPOR/HS_ANIMATIK_FILM_t<n>.json", "KURGU/surumler/KURGU_PLANI_T1_v<N>.json"),
          (R("HS_ANIMATIK", "_RAPOR/HS_ANIMATIK_FILM_t{tur}.json", seyirci=True),), "ai84", "yerel", 3,
          (M("ust_sahip", "kurtarma turu: yapimci·doktor", "yapimci", "doktor"),
           M("kagit_urun", "kapı sağlanmıyor: kâğıt ürün (senaryo + animatik) yüzüne vur raporuyla; videoya geçilmez (§1.4)")),
          None,
          (J("KD", "kurgucu", "duzelt", grup=0, turda="sonra", tasima=(("CIKTI/rapor.json", "KURGU/KURGU_KARARLARI_T1_t{tur}.json"),)),
           B("ZT", "zaman_cizelgesi.py", "--asama", "animatik", grup=1),
           B("SA", "seslendir.py", "--animatik", grup=1, kredili=True),
           B("MU", "muzik.py", "--uret", grup=2),
           B("SK", "ses_katmani.py", "--cizelge", "T1", grup=3),
           B("SM", "son_miks.py", "--animatik", grup=4),
           B("KR", "kurgu_render.py", "--animatik", grup=5, cikti=("ANIMATIK/animatik_v{tur}.mp4",)),
           J("KS", "kesici", "animatik", grup=6, turda="ilk", tasima=(("CIKTI/rapor.json", "KURGU/KESME_T1.json"),)))
          + _seyirci_turu("animatik", "HS_ANIMATIK", "_RAPOR/HS_ANIMATIK_FILM_t{tur}.json", 7),
          butce="animatik_kurgu_tur"),
    Asama("A13", "Kesin bütçe BUT2", "betik kredi.py but2, olcek.py; hat-denetcisi",
          (G("URETIM_ONIZLEME", "A07c", "URETIM_ONIZLEME.json"), G("kuyruk", "A11"), G("OLCUM0", "olcum0"),
           G("animatik imzası", "A12")),
          ("URETIM_ONIZLEME.json", "URETIM_ONIZLEME.md", "_RAPOR/HAT_BUT2.json"),
          (R("BUT2", "_RAPOR/BUT2_FILM.json", butce=True), R("HAT", "_RAPOR/HAT_BUT2.json")), None, "yerel", 1,
          (M("ayni_sahip", "GİTME'nin kapatma koşulu sahibine; sahip düzeltince hat-denetcisi yeni örnekle 1 kez", "hat-denetcisi"),
           M("hedef_alti", "ikinci GİTME güvenlik/bütçe nedenli değilse hedef_alti ile A14a'ya geçilir")), None,
          (B("B2", "kredi.py", "but2", grup=0, cikti=("_RAPOR/BUT2_FILM.json", "URETIM_ONIZLEME.json"), kapi="BUT2"),
           J("HD", "hat-denetcisi", grup=1, persona="BUT2", cikti=("CIKTI/rapor.json",),
             tasima=(("CIKTI/rapor.json", "_RAPOR/HAT_BUT2.json"),), kapi="HAT"))),
    Asama("A14a", "Dikey kesit", "blok_plani --kesit; Memmet elle (kullanıcı GÖNDER'e basar); V1–V3; kesit seyircisi; ders-editoru (PILOT)",
          (G("SAHNELER.json + hareket istemi", "A09", "KAGIT_TAMAM.json"), G("G1 GEÇ görseller", "A11"),
           G("BUT2", "A13", "_RAPOR/BUT2_FILM.json")),
          ("KESIT/kesit_v<N>.mp4", "_RAPOR/PILOT_FILM.json"),
          (R("V2", "_RAPOR/V2_KESIT_t{tur}.json"), R("HS_KESIT", "_RAPOR/HS_KESIT_FILM_t{tur}.json", seyirci=True),
           R("PILOT", "_RAPOR/PILOT_FILM.json")), "flow+ai84", "yerel", 2,
          (DURDU_SIFIR, M("hedef_alti", "PILOT kararı yazılır, A14 hedef_alti ile başlar (§1.5 A14a)")), None,
          (B("BP", "blok_plani.py", "--kesit", grup=0, cikti=("BLOK_PLANI.json",)),
           K("VG", "Masaüstündeki VIDEO_YARI_OTOMATIK.bat'a çift tıkla; açılan Flow sayfasında her istemde GÖNDER'e sen bas. "
                   "Bitince ben kendim devam ederim.", {"tur": "blok", "blok": "KESIT"}, grup=1),
           B("VD", "video_denetim.py", "--klip", "--blok", "KESIT", grup=2, cikti=("_RAPOR/V2_KESIT_t{tur}.json",), kapi="V2"),
           B("SP", "seslendir.py", "--parti", "--kesit", grup=3, kredili=True),
           B("SM", "son_miks.py", "--kesit", grup=4),
           B("KR", "kurgu_render.py", "--kesit", grup=5, cikti=("KESIT/kesit_v{tur}.mp4",)))
          + _seyirci_turu("kesit", "HS_KESIT", "_RAPOR/HS_KESIT_FILM_t{tur}.json", 6, seyirci_kip="kurgu")
          + (J("DE", "ders-editoru", grup=10, persona="PILOT", tasima=(("CIKTI/rapor.json", "_RAPOR/PILOT_DERS.json"),)),
             B("PL", "blok_plani.py", "--pilot-karar", grup=11, cikti=("_RAPOR/PILOT_FILM.json",), kapi="PILOT"))),
    Asama("A14", "Video blokları", "blok_plani → Memmet (elle) → V1/SC1 → film.py bekle --blok → V2, V3, kare_zinciri + G1Z → kuyruk.py",
          (G("SIRALI_GORSEL (G1 GEÇ + SHA1)", "A11"), G("hareket_istem", "A09", "KAGIT_TAMAM.json"),
           G("PILOT_FILM.json", "A14a", "_RAPOR/PILOT_FILM.json")),
          ("SIRALI_VIDEO/NNN.mp4", "KUNYE/NNN.json", "KREDI_DEFTERI.jsonl"),
          (R("V2", "_RAPOR/V2_FILM_t{tur}.json"), R("G1Z", "_RAPOR/G1Z_FILM_t{tur}.json")), "flow", "yerel", 3,
          (M("ayni_sahip", "yonetmen·onarim planı değiştirir", "yonetmen", "onarim"), DURDU_SIFIR), None,
          (B("BP", "blok_plani.py", grup=0, cikti=("BLOK_PLANI.json",)),
           K("VG", "Masaüstündeki VIDEO_YARI_OTOMATIK.bat'a çift tıkla; açılan Flow sayfasında her istemde GÖNDER'e sen bas. "
                   "Blok bitince ben kendim devam ederim.", {"tur": "blok", "blok": "*"}, grup=1),
           B("VD", "video_denetim.py", "--klip", grup=2, cikti=("_RAPOR/V2_FILM_t{tur}.json",), kapi="V2"),
           J("V3", "kare-tarifcisi", "v3", grup=3, adet="blok", tasima=(("CIKTI/rapor.json", "_RAPOR/V3/gozlem_t{tur}_{i}.json"),)),
           B("KZ", "kare_zinciri.py", "--cikar", grup=4, cikti=("_RAPOR/G1Z_FILM_t{tur}.json",), kapi="G1Z"),
           B("KU", "kuyruk.py", "--birlestir", grup=5))),
    Asama("A15", "Ses", "betik seslendir --parti, ses_donustur, ses_karar; gri bantta hikaye-yazari·replik_kabul",
          (G("klipler", "A14"), G("evren sesleri", "evren"), G("diyalog.json", "A12")),
          ("SESLER/diyalog.json", "_RAPOR/S2_FILM.json"), (R("S2", "_RAPOR/S2_FILM_t{tur}.json"),), "flow+ai84", "yerel", 2,
          (DURDU_SIFIR,), None,
          (B("SP", "seslendir.py", "--parti", grup=0, kredili=True),
           B("SD", "ses_donustur.py", grup=1),
           J("RK", "hikaye-yazari", "replik_kabul", grup=2, tasima=(("CIKTI/rapor.json", "_HIKAYE_ODASI/REPLIK_KABUL.json"),)),
           B("SK", "ses_karar.py", grup=3, cikti=("_RAPOR/S2_FILM_t{tur}.json",), kapi="S2"))),
    Asama("A16", "Kurgu", "plan_kurgu, diyalog_esitle, ses_katmani T2, son_miks, kurgu_render, kurgu_denetim (Z3); habersiz-seyirci·kurgu ×3; capcut_film; arsivle",
          (G("videolar", "A14"), G("diyalog.json", "A15", "_RAPOR/S2_FILM_t1.json"), G("raporlar", "A14")),
          ("KURGU/KURGU_PLANI.json", "KURGU/onizleme_v<N>.mp4", "_RAPOR/Z3_v<N>.json", "_RAPOR/HS_KURGU_FILM_t<n>.json",
           "KURGU/son_capcut_projesi.json", "KURGU/altyazi_en.srt"),
          (R("Z3", "_RAPOR/Z3_v{tur}.json"), R("HS_KURGU", "_RAPOR/HS_KURGU_FILM_t{tur}.json", seyirci=True)),
          "flow", "yerel", 3,
          (M("ayni_sahip", "koşullu son tur (son turda GENEL ≥ 0,5 arttıysa): kurgucu·duzelt", "kurgucu", "duzelt"),
           M("hedef_alti", "kural 8: CapCut taslağı açık eksik raporuyla verilir (plan ve zaman koduyla)")), None,
          (J("KD", "kurgucu", "duzelt", grup=0, turda="sonra", tasima=(("CIKTI/rapor.json", "KURGU/KURGU_KARARLARI_T2_t{tur}.json"),)),
           B("PK", "plan_kurgu.py", grup=1),
           B("DE", "diyalog_esitle.py", grup=2),
           B("SK", "ses_katmani.py", "--cizelge", "T2", grup=3),
           B("SM", "son_miks.py", grup=4),
           B("KR", "kurgu_render.py", "--onizleme", grup=5, cikti=("KURGU/onizleme_v{tur}.mp4",)),
           B("KZ", "kurgu_denetim.py", grup=6, cikti=("_RAPOR/Z3_v{tur}.json",), kapi="Z3"),
           J("KS", "kesici", "kurgu", grup=7, turda="ilk", tasima=(("CIKTI/rapor.json", "KURGU/KESME_T2.json"),)))
          + _seyirci_turu("kurgu", "HS_KURGU", "_RAPOR/HS_KURGU_FILM_t{tur}.json", 8)
          + (B("CC", "capcut_film.py", grup=12, cikti=("KURGU/son_capcut_projesi.json",)),
             B("AR", "arsivle.py", "--film", grup=13)),
          butce="animatik_kurgu_tur"),
    Asama("A16n", "Kullanıcı notu", "beceri film-not → taslak_fark, notlari_oku; kurgucu·not; kurgu_uygula; kurgu_denetim --hepsi; capcut_yama",
          (G("kullanıcının notu ya da CapCut düzenlemesi", "kullanici"), G("kurgu", "A16")),
          ("KURGU/TASLAK_FARK.json", "NOTLARIM.json", "NOT_CEVAPLARI.md", "_RAPOR/YAMA_v<N>.json"),
          (R("NOT", "_RAPOR/YAMA_v{tur}.json"),), "flow", "yerel", 1, (HEDEF_ALTI,), None,
          (K("CK", "CapCut'ı kapat. Kapattığını ben kendim görürüm.", {"tur": "dosya_yok", "desen": "KURGU/.capcut_acik"}, grup=0),
           B("TF", "taslak_fark.py", grup=1, cikti=("KURGU/TASLAK_FARK.json",)),
           B("NO", "notlari_oku.py", grup=1),
           J("KN", "kurgucu", "not", grup=2, tasima=(("CIKTI/rapor.json", "NOT_CEVAPLARI.json"),)),
           B("KU", "kurgu_uygula.py", grup=3),
           B("KH", "kurgu_denetim.py", "--hepsi", grup=4),
           B("CY", "capcut_yama.py", grup=5, cikti=("_RAPOR/YAMA_v{tur}.json",), kapi="NOT")),
          istege_bagli=True, kosul="film.py notlar isle"),
    Asama("A17", "Yayın", "capcut_film --yayin; kullanıcı 4K dışa aktarır; kalite_denetim --final; jenerik; kapak; yayin-paketcisi; shorts_mp4; arsivle",
          (G("yayın taslağı", "A16", "KURGU/son_capcut_projesi.json"), G("HIKAYE.json", "A06", "HIKAYE.json"),
           G("KANAL_TESHIS.md", "olcum0")),
          ("YAYIN/<FILM>_4K.mp4", "YAYIN/YAYIN_DOGRULAMA.json", "YAYIN/PAKET.json", "YAYIN/SHORTS/*.mp4"),
          (R("S8", "_RAPOR/S8_FINAL_t{tur}.json"), R("YAYIN", "_RAPOR/YAYIN_PAKET_t{tur}.json")), None, "yerel", 1,
          (M("hedef_alti", "teknik HATA kalırsa yayın paketi 'yayına hazır değil' + nedeni yazar (yükleme kullanıcının işi)"),), None,
          (B("CY", "capcut_film.py", "--yayin", grup=0),
           K("DA", "CapCut'ta 'YZ' ile başlayan en üstteki taslağı aç, 4K 24 fps dışa aktar ve dosyayı filmin YAYIN klasörüne koy. "
                   "Dosyayı görünce ben kendim devam ederim.", {"tur": "dosya_var", "desen": "YAYIN/*_4K.mp4"}, grup=1),
           B("KF", "kalite_denetim.py", "--final", grup=2, cikti=("YAYIN/YAYIN_DOGRULAMA.json", "_RAPOR/S8_FINAL_t{tur}.json"),
             kapi="S8"),
           B("JN", "jenerik.py", grup=3),
           B("KP", "kapak.py", grup=3),
           J("YP", "yayin-paketcisi", "paket", grup=4, cikti=("CIKTI/PAKET.json",), tasima=(("CIKTI/PAKET.json", "YAYIN/PAKET.json"),)),
           J("YK", "yayin-paketcisi", "kapak", grup=4, tasima=(("CIKTI/rapor.json", "YAYIN/KAPAK_SECIM.json"),)),
           B("YD", "yayin_paketi.py", "--dogrula", grup=5, cikti=("_RAPOR/YAYIN_PAKET_t{tur}.json",), kapi="YAYIN"),
           B("SH", "shorts_mp4.py", grup=6),
           B("AR", "arsivle.py", "--film", grup=7))),
    Asama("A17y", "Yükleme (isteğe bağlı)", "betik youtube_yukle.py (kullanıcının YUKLE.bat onayıyla)",
          (G("YAYIN/PAKET.json", "A17", "YAYIN/PAKET.json"), G("YUKLE.bat onayı", "kullanici")), ("YAYIN/YUKLEME.json",),
          (), None, "yerel", 1, (HEDEF_ALTI,), None,
          (B("YY", "youtube_yukle.py", cikti=("YAYIN/YUKLEME.json",)),),
          bulutta_test=False, istege_bagli=True, kosul="izinler.yukleme + YUKLE.bat"),
    Asama("A18", "Kapanış ve öğrenme", "ders_derle; ders-editoru; hikaye-yazari·evren; evren.py --film-sonu; FILM_SONU_RAPORU; yedek; arsivle",
          (G("bütün raporlar", "A17"), G("ders ham kayıtları", "ders_defteri")),
          ("FILM_SONU_RAPORU.md",), (R("DERS", "_RAPOR/DERS_t{tur}.json"),), None, "her_ikisi", 1, (HEDEF_ALTI,), None,
          (B("DD", "ders_derle.py", grup=0),
           J("DE", "ders-editoru", grup=1, tasima=(("CIKTI/rapor.json", "_RAPOR/DERS_ADAY.json"),)),
           J("HE", "hikaye-yazari", "evren", grup=1, tasima=(("CIKTI/rapor.json", "_HIKAYE_ODASI/EVREN_TASLAK.json"),)),
           B("EF", "evren.py", "--film-sonu", grup=2),
           B("DF", "ders_derle.py", "--film-sonu", grup=3, cikti=("FILM_SONU_RAPORU.md", "_RAPOR/DERS_t{tur}.json"), kapi="DERS"),
           B("EY", "evren.py", "--yedekle", grup=4),
           B("AR", "arsivle.py", "--film", grup=5))),
    Asama("A18a", "Yayın sonrası analiz", "betik yayin_analiz.py; yayin-paketcisi·izleme (48 sa, 7 gün, 28 gün)",
          (G("YouTube Studio CSV'si", "youtube"), G("yayın paketi", "A17", "YAYIN/PAKET.json")),
          ("_RAPOR/YAYIN_ANALIZ_<gun>.json",), (), None, "yerel", 1, (HEDEF_ALTI,), None,
          (B("YA", "yayin_analiz.py"), J("YI", "yayin-paketcisi", "izleme", grup=1)),
          bulutta_test=False, istege_bagli=True, kosul="yayından 48 saat sonra; veri yoksa ölçülemedi"),
)

_DIZIN = {a.kod: a for a in ASAMALAR}


def asama(kod): return _DIZIN[kod]


def ana_hat(): return [a for a in ASAMALAR if not a.istege_bagli]


def sira(kod): return [a.kod for a in ASAMALAR].index(kod)


def kip_listesi(s, n):
    """Şablonun kip/persona değerini n örneğe yayar."""
    v = s if isinstance(s, tuple) else (s,) * n
    return [v[i % len(v)] if v else None for i in range(n)]


def denetle(adlar=None):
    """Kayıt tutarlılığı (HATA listesi). adlar: veri/ADLAR.json sözlüğü (verilirse ajan·kip ve kapı adları da denetlenir)."""
    h, gorulen = [], set()
    kodlar = [a.kod for a in ASAMALAR]
    for i, a in enumerate(ASAMALAR):
        if a.kod in gorulen: h.append(f"{a.kod}: iki kez tanımlı")
        gorulen.add(a.kod)
        if not a.tavan_sonrasi: h.append(f"{a.kod}: tavan_sonrasi boş (§1.5: her kapıda zorunlu)")
        for b in a.tavan_sonrasi:
            if b.tur not in BASAMAK_TURLERI: h.append(f"{a.kod}: bilinmeyen basamak türü {b.tur}")
            if not b.aciklama: h.append(f"{a.kod}: basamak açıklaması boş")
            if b.tur in ("ayni_sahip", "ust_sahip") and not b.ajan: h.append(f"{a.kod}: {b.tur} basamağında ajan yok")
        if a.tur_max < 1: h.append(f"{a.kod}: tur_max < 1")
        if a.ortam not in ("her_ikisi", "yerel"): h.append(f"{a.kod}: ortam {a.ortam}")
        if not a.girdiler: h.append(f"{a.kod}: girdi yok")
        for g in a.girdiler:
            if not g.ureten: h.append(f"{a.kod}: '{g.ad}' girdisinin üreteni yok ([SON] S-3)")
            elif g.ureten in kodlar:
                if kodlar.index(g.ureten) >= i: h.append(f"{a.kod}: '{g.ad}' girdisini sonraki aşama {g.ureten} üretiyor")
            elif g.ureten not in DIS_URETICILER: h.append(f"{a.kod}: '{g.ad}' girdisinin üreteni bilinmiyor: {g.ureten}")
        kapi_kodlari = {k.kod for k in a.kapilar}
        if not a.gorevler: h.append(f"{a.kod}: görev şablonu yok")
        for s in a.gorevler:
            if s.tur not in GOREV_TURLERI: h.append(f"{a.kod}/{s.kod}: görev türü {s.tur}")
            if s.turda not in TURDA: h.append(f"{a.kod}/{s.kod}: turda {s.turda}")
            if not (isinstance(s.adet, int) and s.adet >= 1 or s.adet in ADET_ANAHTARLARI): h.append(f"{a.kod}/{s.kod}: adet {s.adet}")
            if s.kapi and s.kapi not in kapi_kodlari: h.append(f"{a.kod}/{s.kod}: kapı {s.kapi} aşamanın kapılarında yok")
            if s.tur == "betik" and not s.arac: h.append(f"{a.kod}/{s.kod}: betik aracı yok")
            if s.tur == "ajan" and not s.ajan: h.append(f"{a.kod}/{s.kod}: ajan adı yok")
            if s.tur == "kullanici" and not (s.mesaj and s.algilama): h.append(f"{a.kod}/{s.kod}: kullanıcı mesajı/algılaması yok")
            if s.kapi and s.tur == "betik" and not any(c == next(k.rapor for k in a.kapilar if k.kod == s.kapi) for c in s.cikti):
                h.append(f"{a.kod}/{s.kod}: kapı raporu görevin çıktıları arasında yok")
        for k in a.kapilar:
            if not any(s.kapi == k.kod for s in a.gorevler): h.append(f"{a.kod}: kapı {k.kod} için görev yok")
        if adlar:
            if a.kod not in adlar.get("asamalar", {}): h.append(f"{a.kod}: ADLAR.json asamalar'da yok")
            ajanlar = adlar.get("ajanlar", {}); kapilar = adlar.get("kapilar", {})
            for s in a.gorevler:
                if s.tur != "ajan": continue
                if s.ajan not in ajanlar: h.append(f"{a.kod}/{s.kod}: ajan {s.ajan} kadroda yok"); continue
                for kp in kip_listesi(s.kip, s.adet if isinstance(s.adet, int) else 1):
                    if kp and kp not in ajanlar[s.ajan].get("kipler", []): h.append(f"{a.kod}/{s.kod}: {s.ajan}·{kp} kipi yok")
            for b in a.tavan_sonrasi:
                if b.ajan and b.ajan not in ajanlar: h.append(f"{a.kod}: basamak ajanı {b.ajan} kadroda yok")
                if b.ajan and b.kip and b.kip not in ajanlar.get(b.ajan, {}).get("kipler", []):
                    h.append(f"{a.kod}: basamak {b.ajan}·{b.kip} kipi yok")
            for k in a.kapilar:
                if k.kod not in kapilar and k.kod not in YEREL_KAPILAR: h.append(f"{a.kod}: kapı {k.kod} ADLAR'da da yerel listede de yok")
    return h


def _hucre(x): return str(x).replace("|", "\\|").replace("\n", " ")


def markdown():
    s = ["# Hat — aşama listesi (üretildi: `film.py asamalar --md`; elle düzenleme)", "",
         "| No | Aşama | Kim | Girdi (üreten) | Çıktı | Kapı | Tur | Tavan sonrası | Kredi | Ortam |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for a in ASAMALAR:
        s.append("| " + " | ".join(_hucre(x) for x in (
            a.kod + (" (isteğe bağlı)" if a.istege_bagli else ""), a.ad, a.kim,
            "; ".join(f"{g.ad} ({g.ureten})" for g in a.girdiler), "; ".join(a.ciktilar),
            ", ".join(k.kod for k in a.kapilar) or "—", a.tur_max,
            " → ".join(f"{b.tur}" + (f" {b.ajan}" + (f"·{b.kip}" if b.kip else "") if b.ajan else "") for b in a.tavan_sonrasi),
            a.kredi or "yok", a.ortam + ("" if a.bulutta_test else " (bulutta test yok)"))) + " |")
    s += ["", "Basamaklar (§1.5): ayni_sahip → ust_sahip → durdu (kurgucu·sifir_kredi) → hedef_alti; feragat edilemeyen HATA "
          "(güvenlik, filtre, kimlik, şema) hiçbir zaman üretime gitmez. Seyirci kapılarında KISMI = kapı sağlandı, hedef değil (§1.4)."]
    return "\n".join(s) + "\n"


def sozluk():
    from dataclasses import asdict
    return [asdict(a) for a in ASAMALAR]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if "--json" in sys.argv: print(json.dumps(sozluk(), ensure_ascii=False, indent=1))
    else: print(markdown())
