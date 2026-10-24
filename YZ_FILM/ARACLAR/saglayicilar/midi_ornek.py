"""MIDI_ORNEK müzik sağlayıcısı — leitmotifin özgün notalarını MIDI'ye yazar ve çalar (TASARIM D-25, §5.6; [SM2] §4.8.4).
Yalnız ANİMATİKTE ve motif omurgası olarak kullanılır; yayın zincirinde tema General MIDI örnekleriyle çalınmaz (muzik_uret düşürür).
Çalıcı: FluidSynth (LGPL, dış ikili) + lisansı LISANSLAR.json'da kayıtlı SF2 (<ses_kutuphanesi>/SF2/*.sf2); ikisi yoksa iç sentez
(numpy toplamsal sentez; kendi kodumuz, lisans sorunu yok) — çıktı kaydında `cal: ic_sentez` yazar.
Kodda: nota_hz("D5") · sentez(notalar, bpm, ...) · midi_yaz(notalar, bpm, yol) · MidiOrnek().muzik(film, ipucu, cikti_dir, aday, motif=...)
"""
import os, re, struct, shutil, subprocess, math
import numpy as np
from saglayicilar import Saglayici

SR = 48000
_ADIM = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_OLCEK = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10], "dorian": [0, 2, 3, 5, 7, 9, 10],
          "phrygian": [0, 1, 3, 5, 7, 8, 10], "lydian": [0, 2, 4, 6, 7, 9, 11], "mixolydian": [0, 2, 4, 5, 7, 9, 10],
          "aeolian": [0, 2, 3, 5, 7, 8, 10], "locrian": [0, 1, 3, 5, 6, 8, 10], "ionian": [0, 2, 4, 5, 7, 9, 11]}


def nota_midi(n):
    m = re.fullmatch(r"([A-Ga-g])([#b]?)(-?\d)", str(n).strip())
    if not m: raise ValueError(f"nota anlaşılmadı: {n!r}")
    return 12 * (int(m.group(3)) + 1) + _ADIM[m.group(1).upper()] + {"#": 1, "b": -1, "": 0}[m.group(2)]


def nota_hz(n): return 440.0 * 2 ** ((nota_midi(n) - 69) / 12.0)


def ton_coz(ton):
    p = (ton or "C major").split(); kok = p[0]
    kip = (p[1] if len(p) > 1 else "major").lower()
    return nota_midi(kok + "3") % 12, _OLCEK.get(kip, _OLCEK["major"])


def _ses(f, sure, sr=SR, tini="flut", genlik=0.25):
    t = np.arange(int(sure * sr)) / sr
    harm = {"flut": (1.0, 0.25, 0.08), "yayli": (1.0, 0.5, 0.33, 0.25, 0.2), "pad": (1.0, 0.3, 0.1)}.get(tini, (1.0, 0.3))
    y = sum(a * np.sin(2 * np.pi * f * (k + 1) * t) for k, a in enumerate(harm)) / sum(harm)
    atak, birak = min(0.04, sure / 4), min(0.12, sure / 3)
    z = np.minimum(1, np.minimum(t / atak, np.maximum(0, (sure - t) / birak)))
    return (genlik * y * z).astype(np.float32)


def sentez(notalar, bpm=72, sr=SR, tini="flut", genlik=0.25):
    """[[nota, vuruş], ...] → mono dizi."""
    vs = 60.0 / float(bpm or 72); parca = []
    for n, v in notalar:
        d = max(0.05, float(v) * vs)
        parca.append(np.zeros(int(d * sr), np.float32) if str(n).upper() in ("R", "-", "REST") else _ses(nota_hz(n), d, sr, tini, genlik))
    return np.concatenate(parca) if parca else np.zeros(0, np.float32)


def eslik(ton, bpm, sure, sr=SR, genlik=0.08):
    """Tonun I–VI–IV–V akorlarıyla yumuşak yatak (stereo)."""
    kok, olcek = ton_coz(ton); vs = 60.0 / float(bpm or 72); akor_sn = 4 * vs
    dizi = [0, 5, 3, 4]; parca = []; t = 0.0; i = 0
    while t < sure:
        d = min(akor_sn, sure - t); der = dizi[i % 4]
        notalar = [48 + kok + olcek[(der + k) % 7] + 12 * ((der + k) // 7) for k in (0, 2, 4)]
        parca.append(sum(_ses(440.0 * 2 ** ((m - 69) / 12.0), d, sr, "pad", genlik) for m in notalar)); t += d; i += 1
    y = np.concatenate(parca) if parca else np.zeros(0, np.float32)
    return np.stack([y, y * 0.92], 1)


def midi_yaz(notalar, bpm, yol, kanal=0, program=73):
    """Standart MIDI dosyası (tip 0) yazar; mido gerekmez. program 73 = flüt (GM)."""
    tpq = 480; ev = bytearray()
    def vlq(n):
        b = [n & 0x7F]; n >>= 7
        while n: b.append((n & 0x7F) | 0x80); n >>= 7
        return bytes(reversed(b))
    us = int(60_000_000 / float(bpm or 72))
    ev += vlq(0) + b"\xff\x51\x03" + us.to_bytes(3, "big") + vlq(0) + bytes([0xC0 | kanal, program])
    bekle = 0
    for n, v in notalar:
        tik = int(round(float(v) * tpq))
        if str(n).upper() in ("R", "-", "REST"): bekle += tik; continue
        m = nota_midi(n)
        ev += vlq(bekle) + bytes([0x90 | kanal, m, 90]) + vlq(tik) + bytes([0x80 | kanal, m, 0]); bekle = 0
    ev += vlq(0) + b"\xff\x2f\x00"
    os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
    with open(yol, "wb") as f:
        f.write(b"MThd" + struct.pack(">IHHH", 6, 0, 1, tpq) + b"MTrk" + struct.pack(">I", len(ev)) + bytes(ev))
    return yol


def _sf2():
    try:
        import ortak
        k = os.path.join(ortak.yollar().get("ses_kutuphanesi") or "", "SF2")
        return sorted(os.path.join(k, f) for f in os.listdir(k) if f.lower().endswith(".sf2"))[:1] if os.path.isdir(k) else []
    except Exception: return []


def _lisansli_sf2():
    try:
        from olcum import ses as O
        return O.lisans("sf2_ses_bankasi").get("dogrulama") not in (None, "bilinmiyor")
    except Exception: return False


class MidiOrnek(Saglayici):
    ad = "midi_ornek"
    turler = ("muzik",)
    kredili = False
    elle = False
    ortam = "her_ikisi"
    yalniz_animatik = True
    model = "midi_ornek 1.0"
    lisans = "özgün motif (ajan) + iç sentez / FluidSynth (LGPL, yalnız çalıştırılır)"

    def cal_yontemi(self):
        return "fluidsynth" if (shutil.which("fluidsynth") and _sf2() and _lisansli_sf2()) else "ic_sentez"

    def muzik(self, film, ipucu, cikti_dir, aday=1, referans_wav=None, motif=None):
        from olcum import ses as O
        os.makedirs(cikti_dir, exist_ok=True)
        ton = (motif or {}).get("ton") or ipucu.get("ton") or "C major"
        bpm = (motif or {}).get("bpm") or ipucu.get("bpm") or 72
        hedef = float(ipucu.get("hedef_sure_sn") or 30)
        out = []
        for i in range(max(1, int(aday))):
            yat = eslik(ton, bpm, hedef)
            if motif and motif.get("notalar"):
                mel = sentez(motif["notalar"], bpm, tini="flut" if i % 2 == 0 else "yayli")
                if self.cal_yontemi() == "fluidsynth":
                    mid = midi_yaz(motif["notalar"], bpm, os.path.join(cikti_dir, f"{ipucu['id']}_motif.mid"))
                    wav = os.path.join(cikti_dir, f"{ipucu['id']}_motif_fs.wav")
                    r = subprocess.run(["fluidsynth", "-ni", "-F", wav, "-r", str(SR), _sf2()[0], mid], capture_output=True)
                    if r.returncode == 0 and os.path.exists(wav): mel = O.mono(O.oku(wav)[0])
                bos = int(len(mel) * 0.25); dongu = np.concatenate([mel, np.zeros(bos, np.float32)])
                tekrar = np.tile(dongu, int(math.ceil(len(yat) / max(1, len(dongu)))))[:len(yat)]
                yat = yat + np.stack([tekrar, tekrar], 1)
            p = os.path.join(cikti_dir, f"{ipucu['id']}_midi{i + 1}.wav")
            O.yaz(p, O.yumusatma(yat * 0.8, ms=20)); out.append(p)
        return out
