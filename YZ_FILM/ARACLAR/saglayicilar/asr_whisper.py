"""FASTER_WHISPER — yerel ASR sağlayıcısı, `asr` türü (TASARIM §5.6; faster-whisper MIT, ağırlıklar bir kez indirilir, sonra
HF_HUB_OFFLINE=1). Kelime zamanlı tanıma; bilinen metin verilirse ve stable-ts (MIT) kuruluysa ona hizalanır (kelime sayısıyla bölme yok).
"""
import os, importlib.util
from saglayicilar import Saglayici, Kisitlandi


class FasterWhisper(Saglayici):
    ad = "faster_whisper"
    turler = ("asr",)
    kredili = False
    elle = False
    ortam = "yerel"
    model = "small.en"
    _m = None

    def hazir(self):
        if importlib.util.find_spec("faster_whisper") is None: return False, "faster-whisper kurulu değil (KUR1)"
        return True, ""

    def _model(self):
        if FasterWhisper._m is None:
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            from faster_whisper import WhisperModel
            FasterWhisper._m = WhisperModel(self.model, device="cpu", compute_type="int8")
        return FasterWhisper._m

    def asr(self, film, wav, bilinen_metin=None):
        if bilinen_metin and importlib.util.find_spec("stable_whisper") is not None:
            try:
                import stable_whisper
                r = stable_whisper.load_faster_whisper(self.model, device="cpu", compute_type="int8").align(wav, bilinen_metin, language="en")
                kel = [{"w": w.word.strip(), "bas": round(w.start, 3), "bit": round(w.end, 3),
                        "guven": round(getattr(w, "probability", 1.0) or 1.0, 3)} for s in r.segments for w in s.words]
                serbest = self.asr(film, wav)
                return {"metin": serbest["metin"], "kelimeler": kel, "guven": serbest["guven"], "hizalama": "stable-ts"}
            except Exception: pass
        try: segs, _ = self._model().transcribe(wav, word_timestamps=True, language="en", vad_filter=True)
        except Exception as e: raise Kisitlandi(f"ASR çalışmadı: {str(e)[:100]}", kod="hazir_degil") from None
        kel = [{"w": w.word.strip(), "bas": round(w.start, 3), "bit": round(w.end, 3), "guven": round(w.probability, 3)}
               for s in segs for w in (s.words or [])]
        g = sum(k["guven"] for k in kel) / len(kel) if kel else 0.0
        return {"metin": " ".join(k["w"] for k in kel), "kelimeler": kel, "guven": round(g, 3)}
