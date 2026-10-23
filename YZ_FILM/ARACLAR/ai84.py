"""AI84.pro (ElevenLabs aracısı) istemcisi. Anahtar dosyadan okunur, asla yazdırılmaz."""
import json, os, time, urllib.request, urllib.parse, uuid

BASE = "https://api.ai84.pro"
_AYARLAR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AYARLAR")
def _dolu(p): return os.path.exists(p) and bool(open(p, encoding="utf-8-sig").read().strip())
KEY_FILE = os.environ.get("AI84_KEY_FILE") or next(
    (p for p in (os.path.join(_AYARLAR, "ai84_anahtar.txt"), os.path.join(os.path.expanduser("~"), "Desktop", "ai84_anahtar.txt"))
     if _dolu(p)), os.path.join(_AYARLAR, "ai84_anahtar.txt"))
if not _dolu(KEY_FILE):
    raise SystemExit(f"AI84 anahtarı yok. ai84.pro'daki API anahtarını şu dosyanın İLK SATIRINA yapıştırıp kaydet: {KEY_FILE}")
_KEY = open(KEY_FILE, encoding="utf-8-sig").read().strip().splitlines()[0].strip()
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


class AI84Error(Exception):
    pass


def _req(method, path, body=None, params=None, headers=None, raw=False, timeout=120):
    url = BASE + path + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
    h = {"xi-api-key": _KEY, **UA, **(headers or {})}
    data = None
    if body is not None and not isinstance(body, bytes):
        data = json.dumps(body).encode(); h["Content-Type"] = "application/json"
    elif isinstance(body, bytes):
        data = body
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            b = resp.read()
            return b if raw else json.loads(b)
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")[:300]
        raise AI84Error(f"{e.code} {path}: {msg}") from None


def credits():
    return _req("GET", "/v1/credits")["credits"]


def models():
    return _req("GET", "/v1/models", params={"tts_only": "true"})["data"]


def voices(**filters):
    return _req("GET", "/v1/shared-voices", params={"page_size": 30, "page": 0, **filters})["voices"]


def estimate(service, base_amount, **options):
    return _req("POST", "/v1/estimate-credit-cost", {"serviceType": service, "provider": "elevenlabs",
                                                "baseAmount": base_amount, "options": options})


def _poll(path, key="job", timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            j = _req("GET", path)
        except AI84Error as e:
            if str(e).startswith("5"): time.sleep(4); continue
            raise
        job = j.get(key, j)
        st = job.get("status")
        if st == "done": return job
        if st in ("failed", "error"):
            raise AI84Error(f"iş başarısız: {job.get('errorMessageKey') or job.get('error_message_key')} {job.get('errorMessage') or job.get('error_message')}")
        time.sleep(3)
    raise AI84Error("zaman aşımı")


def _download(url, out):
    r = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(r, timeout=300) as resp, open(out, "wb") as f:
        f.write(resp.read())
    return out


def tts(text, voice_id, out, model_id="eleven_v4", settings=None, lang="en"):
    body = {"text": text, "voice_id": voice_id, "model_id": model_id, "language_code": lang}
    if settings: body["voice_settings"] = settings
    j = _req("POST", "/v2/text-to-speech/async", body)
    job = _poll(f"/v2/text-to-speech/async/{j['job_id']}")
    _download(job["audioUrl"], out)
    return job.get("credit_cost")


def voice_change(audio_path, voice_id, out, model_id=None, settings=None, remove_noise=False):
    b = "----ai84" + uuid.uuid4().hex
    parts = []
    def field(n, v): parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode())
    field("voice_id", voice_id)
    if model_id: field("model_id", model_id)
    if settings: field("voice_settings", json.dumps(settings))
    field("remove_background_noise", "true" if remove_noise else "false")
    fn = os.path.basename(audio_path)
    ctype = {".wav": "audio/wav", ".m4a": "audio/mp4"}.get(os.path.splitext(fn)[1].lower(), "audio/mpeg")
    parts.append(f'--{b}\r\nContent-Disposition: form-data; name="audio"; filename="{fn}"\r\nContent-Type: {ctype}\r\n\r\n'.encode()
                 + open(audio_path, "rb").read() + b"\r\n")
    parts.append(f"--{b}--\r\n".encode())
    j = _req("POST", "/v2/voice-changer", b"".join(parts), headers={"Content-Type": f"multipart/form-data; boundary={b}"}, timeout=600)
    job = _poll(f"/v2/voice-changer/{j['job_id']}")
    _download(job["outputAudioUrl"], out)
    return job.get("creditCost")
