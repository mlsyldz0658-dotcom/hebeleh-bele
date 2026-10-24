"""KUTUPHANE — lisansı kayıtlı müzik parçaları (KUR1 çekirdek seti + isteğe bağlı YouTube Ses Kitaplığı), `muzik` türü (TASARIM D-25).
Dizin: <ses_kutuphanesi>/MUZIK/DIZIN.json  {"<göreli yol>": {lisans, ticari_youtube: evet|hayir|bilinmiyor, etiketler[], bpm, ton,
  sure_sn, sha1, kaynak_url, atif}}. Yalnız ticari_youtube = "evet" olan parçalar aday olur; kurulum dosyayı sabit adres + SHA-1 ile indirir
(film başına indirme yok). Aday: ipucunun duygu/tür/istem kelimeleriyle etiket örtüşmesi en yüksek parçalar; hedef süreye kırpılır ya da
döngülenir (uç yumuşatma 20 ms). Seçilen adayın kaynak kaydı yanına `<aday>.kaynak.json` olarak yazılır (KAYNAK_KAYDI'na girer).
"""
import os, re, json
import numpy as np
from saglayicilar import Saglayici, Kisitlandi


def dizin_yolu():
    import ortak
    return os.path.join(ortak.yollar().get("ses_kutuphanesi") or "", "MUZIK", "DIZIN.json")


def dizin():
    try:
        with open(dizin_yolu(), encoding="utf-8-sig") as f: d = json.load(f)
    except Exception: return {}
    return {k: v for k, v in d.items() if isinstance(v, dict) and v.get("ticari_youtube") == "evet" and not v.get("kara_liste")}


class Kutuphane(Saglayici):
    ad = "kutuphane"
    turler = ("muzik",)
    kredili = False
    elle = False
    ortam = "her_ikisi"
    model = "kutuphane"
    lisans = "parça başına (DIZIN.json)"

    def hazir(self):
        try: d = dizin()
        except Exception as e: return False, str(e)[:100]
        return (True, "") if d else (False, "müzik çekirdek seti yok ya da lisanslı parça yok (KUR1; LISANSLAR.json muzik_cekirdek_seti)")

    def muzik(self, film, ipucu, cikti_dir, aday=3, referans_wav=None, motif=None):
        from olcum import ses as O
        d = dizin()
        if not d: raise Kisitlandi("kütüphane boş", kod="hazir_degil")
        kok = os.path.dirname(dizin_yolu())
        ist = set(re.findall(r"[a-zçğıöşü]+", " ".join(str(ipucu.get(k) or "") for k in ("duygu", "tur", "istem_en")).lower()))
        sira = sorted(d.items(), key=lambda kv: -len(ist & {e.lower() for e in kv[1].get("etiketler") or []}))
        hedef = float(ipucu.get("hedef_sure_sn") or 30); os.makedirs(cikti_dir, exist_ok=True); out = []
        for i, (rel, kay) in enumerate(sira[:int(aday)]):
            x, sr = O.oku(os.path.join(kok, rel)); x = O.stereo(x); n = int(hedef * sr)
            if len(x) < n: x = np.concatenate([x] * (n // max(1, len(x)) + 1))
            p = os.path.join(cikti_dir, f"{ipucu['id']}_kut{i + 1}.wav")
            O.yaz(p, O.yumusatma(x[:n], sr, 20))
            with open(p + ".kaynak.json", "w", encoding="utf-8") as f:
                json.dump(dict(kay, dosya=rel, saglayici=self.ad), f, ensure_ascii=False)
            out.append(p)
        return out
