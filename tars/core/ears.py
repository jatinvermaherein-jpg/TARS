"""The hearing pipeline: VAD -> engine ladder -> transcript -> dialog.

Flow law (contract §3): a `transcript` bus event {who, text} fires BEFORE the
reply is routed, so the app shows what was heard, dimmed. Bad-audio honesty: a
segment that holds no speech never executes — the §22 "heard badly" canon line
answers instead. The ears never touch the mic directly: bytes come from a
capture adapter, and capture.py enforces the mic-cold law.

VAD semantics (pinned, declared): 30ms frames, RMS >= 500 marks speech,
silence gaps <= 270ms bridge into one span, spans under 90ms are dropped.

Engine protocol (declared): load() once -> bool, transcribe(pcm) -> str ("" =
nothing heard); a raised RuntimeError or a False load falls to the next
engine. Ladder: WhisperSmallLocal -> GroqEarsAdapter; an all-drained ring
answers the canon all-spent line.
"""
import math
from array import array

from tars.core import canon, voicefix

FRAME_MS = 30
RMS_THRESHOLD = 500.0
HANGOVER_MS = 270   # silence this short inside speech bridges into one span
MIN_SPEECH_MS = 90  # blips shorter than this are mouth-clicks, not words


def frame_rms(frame: bytes) -> float:
    samples = array("h")
    samples.frombytes(frame)
    if not samples:
        return 0.0
    return math.sqrt(sum(s * s for s in samples) / len(samples))


def vad_spans(pcm_bytes: bytes, rate: int = voicefix.RATE) -> list:
    """[(start_ms, end_ms)] speech spans over 16-bit mono PCM — exact, deterministic."""
    frame_bytes = 2 * rate * FRAME_MS // 1000
    hangover_frames = HANGOVER_MS // FRAME_MS
    speech_flags = [frame_rms(pcm_bytes[i:i + frame_bytes]) >= RMS_THRESHOLD
                    for i in range(0, len(pcm_bytes) - frame_bytes + 1, frame_bytes)]
    spans = []
    run_start = None
    last_speech = None
    for index, voiced in enumerate(speech_flags):
        if voiced:
            if run_start is None:
                run_start = index
            last_speech = index
        elif run_start is not None and index - last_speech > hangover_frames:
            spans.append((run_start * FRAME_MS, (last_speech + 1) * FRAME_MS))
            run_start = None
            last_speech = None
    if run_start is not None:
        spans.append((run_start * FRAME_MS, (last_speech + 1) * FRAME_MS))
    return [(start, end) for start, end in spans if end - start >= MIN_SPEECH_MS]


def slice_pcm(pcm_bytes: bytes, span: tuple, rate: int = voicefix.RATE) -> bytes:
    start_b = 2 * rate * span[0] // 1000
    end_b = 2 * rate * span[1] // 1000
    return pcm_bytes[start_b:end_b]


class WhisperSmallLocal:
    """Local whisper-small. Lazy-loads a declared model path; the RAM Charter
    policy is checked at load — if the burst would cross the ceiling, the
    ladder falls to Groq-ears instead of squeezing the family's RAM."""

    MODEL_NAME = "whisper-small"   # the declared model slot (M-1 stages the file under the data root)
    BURST_MB = 900                 # bible §28: whisper bursts 0.8–1GB transient

    def __init__(self, model_dir, ceiling_mb: int = 2000, ram_probe=None):
        self._model_path = model_dir / "whisper-small.bin"
        self._ceiling_mb = ceiling_mb
        self._ram_probe = ram_probe or current_ram_mb
        self._loaded = False

    def load(self) -> bool:
        if self._loaded:
            return True
        if not self._model_path.exists():
            return False  # canon: the model file arrives at M-1; absent here, the ladder steps down
        if self._ram_probe() + self.BURST_MB > self._ceiling_mb:
            return False  # RAM Charter policy: do the math, fall to Groq-ears under pressure
        try:
            from faster_whisper import WhisperModel  # staged on the AiO at M-1; absent in the sandbox
        except ImportError:
            return False  # canon: dependency lives on the AiO, never in a sandbox
        self._model = WhisperModel(str(self._model_path), device="cpu", compute_type="int8")
        self._loaded = True
        return True

    def transcribe(self, pcm_bytes: bytes) -> str:
        segments, _info = self._model.transcribe(io_bytes(pcm_bytes), beam_size=1)
        return " ".join(segment.text.strip() for segment in segments).strip()


class GroqEarsAdapter:
    """Groq whisper-large-v3-turbo backup ear. Bills a ring key ONLY through
    keys.py (the ears lane, LANE_CAPS wired there); the wire body is real and
    reviewable but never network-called in a sandbox — tests inject the
    transport at the declared seam."""

    URL = "https://api.groq.com/openai/v1/audio/transcriptions"
    MODEL = "whisper-large-v3-turbo"

    def __init__(self, ring, transport=None):
        self._ring = ring
        self._transport = transport or _multipart_post

    def load(self) -> bool:
        return True  # nothing to warm up; the ring answers availability

    def transcribe(self, pcm_bytes: bytes) -> str:
        key = self._ring.next_key("groq", "ears")
        if key is None:
            raise RuntimeError("ears lane drained")  # the ladder maps this to the canon all-spent line
        body, content_type = build_multipart(
            {"model": self.MODEL}, "file", "speech.wav", voicefix.wrap_wav(pcm_bytes), "audio/wav")
        text = self._transport(self.URL, body, content_type, key.key)
        key.record("ears")  # billing travels through the ring alone; the vault ledger belongs to the router
        return text


def io_bytes(pcm_bytes: bytes) -> bytes:
    """Whisper consumes a decodable container; PCM gets wrapped at the edge."""
    return voicefix.wrap_wav(pcm_bytes)


def build_multipart(fields: dict, file_field: str, filename: str, file_bytes: bytes,
                    file_content_type: str) -> tuple:
    """RFC 7578 multipart body for the transcription endpoint (stdlib, hand-packed)."""
    boundary = "----tars-ear-boundary"
    chunks = []
    for name, value in fields.items():
        chunks.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode("utf-8"))
    chunks.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; "
                   f"filename=\"{filename}\"\r\nContent-Type: {file_content_type}\r\n\r\n").encode("utf-8"))
    chunks.append(file_bytes)
    chunks.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def _multipart_post(url: str, body: bytes, content_type: str, key_string: str) -> str:
    """The real wire body — reviewable, never called keyless, first fired at the P3 ceremony."""
    import json
    import socket
    import urllib.error
    import urllib.request
    if not key_string:
        raise RuntimeError("ears call attempted without a key")  # belt-and-braces: the ring normally stops this
    request = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {key_string}", "Content-Type": content_type})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, TimeoutError,
            ConnectionError, OSError, json.JSONDecodeError, KeyError) as exc:
        raise RuntimeError(f"groq ears call failed: {type(exc).__name__}") from exc
    return payload["text"]


class FixtureEarEngine:
    """Scripted ear: transcripts pop in order; load() follows the script flag."""

    def __init__(self, script: list, loads: bool = True):
        self._script = list(script)
        self._loads = loads
        self.calls = 0
        self.load_calls = 0

    def load(self) -> bool:
        self.load_calls += 1
        return self._loads

    def transcribe(self, pcm_bytes: bytes) -> str:
        self.calls += 1
        step = self._script.pop(0)
        if step == "fail":
            raise RuntimeError("scripted ear failure")
        return step


class EarLadder:
    """One load() per engine, cached; transcribe walks the order until one serves."""

    def __init__(self, engines: list, log):
        self._engines = engines
        self._loaded = {}
        self._log = log

    def transcribe(self, pcm_bytes: bytes):
        for engine in self._engines:
            name = type(engine).__name__
            if name not in self._loaded:
                self._loaded[name] = engine.load()
            if not self._loaded[name]:
                continue
            try:
                return engine.transcribe(pcm_bytes)
            except RuntimeError as exc:
                self._log.entry("ears", engine=name, failed=str(exc))  # a dead engine steps down, never crashes
        return None


def run_voice_turn(capture, ladder: EarLadder, machine, bus, dialog, mouth=None) -> dict:
    """One push-to-talk utterance, end to end. LISTENING-first: a mouth in
    flight is interrupted (a fresh listen wins, §20), then the law-guarded
    capture streams frames while the machine stays in LISTENING."""
    if mouth is not None:
        mouth.interrupt()
    if machine.state == "armed":
        machine.voice_start()
    if machine.state != "listening":
        return {"ok": False, "line": canon.LINE_CATCH_ALL}
    frames = []
    opened = capture.open()
    try:
        for frame in capture.frames():
            frames.append(frame)
    finally:
        capture.close()  # mic goes cold on ANY exit path — law, not habit
    if machine.state != "listening":
        return {"ok": False, "line": canon.LINE_CATCH_ALL}  # kill mid-capture: the turn dies with the machine (Law 5)
    if not opened:
        machine.heard()
        dialog.emit_line(canon.LINE_NO_MIC)  # §22 row 12: device absent, the text path stays home
        return {"ok": False, "line": canon.LINE_NO_MIC}
    spans = vad_spans(b"".join(frames))
    transcripts = []
    for span in spans:
        text = ladder.transcribe(slice_pcm(b"".join(frames), span))
        if text is None:
            machine.heard()
            dialog.emit_line(canon.LINE_ALL_SPENT)
            return {"ok": False, "line": canon.LINE_ALL_SPENT}
        if text.strip():
            transcripts.append(text.strip())
    if not transcripts:
        machine.heard()
        dialog.emit_line(canon.LINE_HEARD_BADLY)
        return {"ok": False, "line": canon.LINE_HEARD_BADLY}
    heard = " ".join(transcripts)
    machine.heard()
    bus.emit("transcript", {"who": machine.audience, "text": heard})  # shown dimmed BEFORE routing — contract §3
    return {"ok": True, "text": heard, "chatId": dialog.send_voice(heard)["chatId"]}


def current_ram_mb() -> int:
    """Process RSS probe for the whisper RAM policy — os-adapted."""
    import os
    if os.name == "nt":
        # canon: Windows reads RSS via psapi ctypes on the AiO
        import ctypes
        counters = ctypes.create_string_buffer(40)
        ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),
                                                 ctypes.byref(counters), 40)
        return int.from_bytes(counters[16:24], "little") // (1024 * 1024)
    with open("/proc/self/statm", "r", encoding="ascii") as statm:
        return int(statm.read().split()[1]) * 4096 // (1024 * 1024)  # canon: Linux probe — the sandbox's one
