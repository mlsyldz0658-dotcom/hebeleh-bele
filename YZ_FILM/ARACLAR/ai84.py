"""AI84.pro (ElevenLabs aracısı) istemcisi. Anahtar dosyadan okunur, asla yazdırılmaz.
Anahtar ilk istekte okunur (tembel): anahtarsız `import ai84` süreci öldürmez; istek anında anahtar yoksa AI84Error.
Yer: AI84_KEY_FILE ortam değişkeni ya da <veri>/AYARLAR/ai84_anahtar.txt (ortak.yollar)."""
import json, os, time, urllib.request, urllib.parse, uuid
import ortak

BASE = "https://api.ai84.pro"
_KEY = None


def _dolu(p):
    try:
        with open(p, encoding="utf-8-sig") as f: return bool(f.read().strip())
    except OSError: return False


def anahtar_dosyasi():
    if os.environ.get("AI84_KEY_FILE"): return os.environ["AI84_KEY_FILE"]
    p = os.path.join(ortak.yollar()["ayarlar"], "ai84_anahtar.txt")
    yedek = os.path.join(os.path.expanduser("~"), "Desktop", "ai84_anahtar.txt")
    return p if _dolu(p) or not _dolu(yedek) else yedek


def _anahtar():
    global _KEY
    if _KEY is None:
        try: p = anahtar_dosyasi()
        except ortak.YolYok as e: raise AI84Error(str(e)) from None
        if not _dolu(p):
            raise AI84Error(f"AI84 anahtarı yok. ai84.pro'daki API anahtarını şu dosyanın İLK SATIRINA yapıştırıp kaydet: {p}")
        with open(p, encoding="utf-8-sig") as f: _KEY = f.read().strip().splitlines()[0].strip()
    return _KEY


UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


class AI84Error(Exception):
    pass


def _req(method, path, body=None, params=None, headers=None, raw=False, timeout=120):
    url = BASE + path + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
    h = {"xi-api-key": _anahtar(), **UA, **(headers or {})}
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
