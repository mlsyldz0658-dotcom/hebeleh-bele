"""ÇEKİM LİSTESİ — parti başına okunur çekim listesi: plan eleştirmeni, üretilebilirlik ve süreklilik denetçileri (A07d) ve insan için
(TASARIM §6.4, §1.3 A07c–A07d, [SON] S-3; [YN2] §4.6.1).

Kullanım (film.py calis çağırır: "<arac> <args> --film <film>"):
  python cekim_listesi.py --film <film> [--parti 1]     → _YONETMEN/CEKIM_LISTESI_P<n>.md (parti başına)
Kodda: liste(kok, parti) → markdown metni
İçerik (sahne başına): mekân, zaman, sahne tipi, eksen ve kamera tarafı, ışık, kroki PNG'si (_YONETMEN/KROKI/<mekan>.png), sözleşme
  giriş/çıkış özeti; plan başına tablo satırı (kod, no, kadraj + kurulum, plan tipi, kullanılan süre, kesme) ve altında TR görünür tarif
  (plan_dili "cekim"; saniyeli adımlar), başlangıç ve bitiş karesinin olgu özeti (dünya defteri), dış ifade, replik, derlenmiş hareket
  istemi (varsa) ve o planın Z0/K0 bulguları. Bu liste yazar ve denetçi içindir (amaç dahil); kör paket DEĞİLDİR (kor_paket.py).
Çıkış kodları: 0 tamam · 1 bozuk girdi · 2 SAHNELER.json yok · 4 kullanım.
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, plan_ortak as po

SURUM = "cekim_listesi 1.0"
BULGU_RAPORLARI = ("_RAPOR/K0_FILM.json", "_RAPOR/Z0_FILM.json", "_RAPOR/ZAMAN_T0.json")


def _sn(x): return ("%.1f" % float(x)).replace(".", ",") if isinstance(x, (int, float)) else "?"


def bulgular(kok):
    out = {}
    for rel in BULGU_RAPORLARI:
        r = ortak.json_oku(os.path.join(kok, rel), {}) or {}
        for b in (r.get("hatalar") or []) + (r.get("bayraklar") or []):
            out.setdefault(b.get("plan"), []).append(f"{r.get('kapi')} {b.get('seviye')} {b.get('madde')}" + (f" ({b.get('kural')})" if b.get("kural") else ""))
    return out


def liste(kok, s, parti, B, D, bul):
    ps = po.sozluk("plan"); ifd = po.sozluk("ifade").get("degerler") or {}
    import plan_dili as pd
    P = sorted([p for p in s.get("sahneler") or [] if int(p.get("parti") or 1) == parti], key=lambda p: float(p.get("sira", p.get("no", 0)) or 0))
    gruplar = s.get("sahne_gruplari") or {}
    sat = [f"# Çekim listesi — {s.get('film') or os.path.basename(kok)} · Parti {parti}", "",
           f"{len(P)} plan · toplam {_sn(sum(float((p.get('kullanim') or {}).get('sure') or 0) for p in P))} sn kullanılan süre · üreten {SURUM}", "",
           "Sağ/sol karakterin KENDİ sağı/soludur. Süreler klip içindeki saniyedir (8 sn klip). Bu liste denetçi içindir; seyirciye gitmez.", ""]
    for sid in dict.fromkeys((p.get("zanaat") or {}).get("sahne_grubu") for p in P):
        sg = gruplar.get(sid) or {}; z0 = sg.get("zaman") or {}; isik = sg.get("isik") or {}
        sat += [f"## {sid} — {sg.get('mekan') or '?'} · {sg.get('sahne_tipi') or '?'}", "",
                f"- Zaman: gün {z0.get('gun', '?')}, {z0.get('gun_saati') or z0.get('saat') or '?'}, hava {z0.get('hava') or '-'}; atlama {z0.get('atlama') or 'yok'}",
                f"- Eksen: {' – '.join(sg.get('eksen') or []) or 'yok'} · kamera tarafı: {sg.get('kamera_tarafi') or '-'} · kalıp: {sg.get('kalip') or '-'}",
                f"- Işık: ana {isik.get('ana') or '-'}, dolgu {isik.get('dolgu') or '-'}, arka {isik.get('arka') or '-'}",
                f"- Kroki: `_YONETMEN/KROKI/{sg.get('mekan')}.png`" + ("" if os.path.isfile(os.path.join(kok, "_YONETMEN", "KROKI", f"{sg.get('mekan')}.png")) else " (henüz çizilmedi)"),
                f"- Hedef: {sg.get('plan_hedef', '?')} plan, {sg.get('sure_hedef_sn', '?')} sn · yasaklar: {', '.join(sg.get('yasaklar') or []) or '-'}", ""]
        sat += ["| # | Kod | Kadraj · kurulum | Tip | Kullanılan | Kesme | Zincir |", "|---|---|---|---|---|---|---|"]
        sp = [p for p in P if (p.get("zanaat") or {}).get("sahne_grubu") == sid]
        for p in sp:
            z = p.get("zanaat") or {}; k = z.get("kamera") or {}; ks = z.get("kesme") or {}; zn = z.get("zincir") or {}; ku = p.get("kullanim") or {}
            kad = ((ps.get("kadraj") or {}).get(k.get("kadraj")) or {}).get("tr", k.get("kadraj"))
            sat.append(f"| {p.get('no')} | {z.get('kod')} | {kad} · {k.get('kurulum')} · {k.get('hareket_tipi') or 'sabit'} | {z.get('plan_tipi')} | "
                       f"{_sn(ku.get('bas'))}+{_sn(ku.get('sure'))} sn | {ks.get('tip') or '-'}" + (f" ({_sn(ks.get('ses_tasma_sn'))} sn)" if ks.get("ses_tasma_sn") else "")
                       + f" | {zn.get('gecis_turu') or '-'} / {zn.get('baslangic') or '-'}" + (" · Bitir" if zn.get("bitis_sabitle") else "") + " |")
        sat.append("")
        for p in sp:
            z = p.get("zanaat") or {}; no = p.get("no"); d = (D.get("planlar") or {}).get(str(no)) or {}
            sat.append(f"### {no} · {z.get('kod')}")
            sat += [f"- {x}" for x in pd.gorunur_tarif(p, "cekim", B)]
            if d.get("bas_ozet"): sat.append(f"- Başlangıç karesi: {d['bas_ozet']}")
            if d.get("bit_ozet"): sat.append(f"- Bitiş (sonraki klibin başı): {d['bit_ozet']}")
            for kim, o in (z.get("oyunculuk") or {}).items():
                di = (o or {}).get("dis_ifade") or {}
                tr = lambda v: (ifd.get(v) or {}).get("tr") or v
                sat.append(f"- Oyunculuk {kim}: {tr(di.get('bas'))} → {tr(di.get('bit'))}" + (f"; alt metin: {o.get('alt_metin')}" if o.get("alt_metin") else ""))
            r = p.get("replik") or {}
            if r.get("metin"): sat.append(f"- Replik {r.get('id')} ({r.get('karakter')}, {r.get('teslim') or '-'}): \"{r['metin']}\"")
            if z.get("ekranda_bilgi"): sat.append(f"- Ekranda: {z['ekranda_bilgi']}")
            if p.get("hareket_istem"): sat.append(f"- Hareket istemi (EN): `{p['hareket_istem']}`")
            for b in bul.get(no) or []: sat.append(f"- Bulgu: {b}")
            sat.append("")
    film_b = bul.get(None) or []
    if film_b: sat += ["## Film düzeyi bulgular", ""] + [f"- {b}" for b in film_b] + [""]
    return "\n".join(sat)


def main(argv):
    if "-h" in argv or "--help" in argv or "--film" not in argv: print(__doc__); return 4
    kok = po.film_kok(po.arg_al(argv, "--film"))
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    if not isinstance(s, dict): print("!! SAHNELER.json yok", flush=True); return 2
    if int(s.get("_surum", 1) or 1) < 2: print("!! v1 SAHNELER: çekim listesi v2 ister", flush=True); return 1
    import plan_dili
    B = plan_dili.baglam(kok, s); D = ortak.json_oku(os.path.join(kok, "DUNYA_DEFTERI.json"), {}) or {}; bul = bulgular(kok)
    istek = po.arg_al(argv, "--parti")
    partiler = [int(istek)] if istek else sorted({int(p.get("parti") or 1) for p in s.get("sahneler") or []})
    for n in partiler:
        yol = os.path.join(kok, "_YONETMEN", f"CEKIM_LISTESI_P{n}.md")
        metin = liste(kok, s, n, B, D, bul)
        os.makedirs(os.path.dirname(yol), exist_ok=True); tmp = yol + ".tmp"
        with open(tmp, "w", encoding="utf-8", newline="\n") as f: f.write(metin + "\n")
        os.replace(tmp, yol)
        print(f"çekim listesi: {os.path.relpath(yol, kok)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
