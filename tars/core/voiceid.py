"""Cooper ID — the recognizer and the 16-row §22 matrix engine.

HONEST LABEL (bible §22, told plainly and kept in code): voice ID here is
CONVENIENCE-GRADE — like face-unlock on a phone, not a password. A good
recording can fool it. That is why dangerous intents always demand live
confirmation + passphrase — layers, not paranoia. Nothing below claims more.

Embedding engine protocol: embed(pcm) -> vector, score(vector, profile) ->
cosine 0..1. ResemblyzerScorer is the real nt-guarded path (M-1 staged);
FixtureScorer is a deterministic in-code spectral embedding (frame spectra
over a declared 20Hz grid, Hann-windowed, per-frame normalized votes) so the
entire matrix is fixture-provable with voicefix tones: enrolled voice = its
carrier frequency, a cold = the declared Hz drift, a stranger = a far carrier.
Recognition NEVER crosses the bridge: list_members() omits embeddings.

THE MATRIX (bible line 209, byte-for-byte): MATRIX_ROWS is the single
reviewable table; every row is triggered by the selftest. Two rows honestly
carry NO special line: three-fails (the lock itself; the third failure's own
row line answers) and recording-attack (detected unreliably — the confirm
layers are the protection). Side-effects ride state.py + audience only.
"""
import hashlib
import json
import math
from array import array
from pathlib import Path

from tars.core import canon, voicefix
from tars.core.ears import RMS_THRESHOLD, EarLadder, finish_voice_turn, frame_rms, slice_pcm, vad_spans

# The 16-row error matrix — bible §22 line 209, verbatim. None = honestly NO special line.
MATRIX_ROWS = (
    ("verified", canon.LINE_VERIFIED),                # verified -> "Cooper."
    ("unknown", canon.LINE_GUEST),                    # unknown voice -> guest rules line
    ("borderline", canon.LINE_VOICE_UNCERTAIN),       # borderline -> "Voice uncertain. Passphrase, please."
    ("three-fails", None),                            # 3 fails -> session lock to guest; pass (spoken OR typed) restores Tier-1 even mid-lock
    ("silence-x3", canon.LINE_EXIT),                  # silence three turns running -> stand down
    ("noise", canon.LINE_NOISE),                      # loud broadband rush -> "Too much noise to hear you."
    ("low-confidence", canon.LINE_HEARD_BADLY),       # heard badly -> never execute a guessed transcript
    ("two-voices", canon.LINE_TWO_VOICES),            # overlapping speakers -> "One at a time, please."
    ("recording-attack", None),                       # NO special line — detected unreliably; confirm layers protect
    ("enrollment-fail", canon.LINE_VOICEPRINT_UNCLEAR),
    ("no-mic", canon.LINE_NO_MIC),
    ("mic-denied", canon.LINE_MIC_DENIED),
    ("cloud-fail", canon.LINE_CLOUD_FAIL),            # the four §11 rows close the matrix
    ("keys-spent", canon.LINE_ALL_SPENT),
    ("no-network", canon.LINE_NO_NETWORK),
    ("catch-all", canon.LINE_CATCH_ALL),
)


def matrix_line(row: str):
    """The matrix as data: the canon line a row speaks, or None where the bible speaks none."""
    return dict(MATRIX_ROWS)[row]  # the table is closed on purpose: an unknown row name is a bug, not a case

# Declared fixture-embedding geometry (all values pinned by the selftest).
SPECTRAL_CENTERS = tuple(100 + 20 * i for i in range(26))  # 100..600Hz, 20Hz grid
FRAME_SAMPLES = 480                                        # 30ms at 16kHz
EMBED_MIN_RMS = RMS_THRESHOLD                              # a frame must be audible to vote
TWO_VOICE_MIN_SECOND_RATIO = 0.30   # second spectral summit this strong = another speaker is talking
TWO_VOICE_PEAK_TOP = 0.40           # a duet's summits stay above this; broadband rush plateaus below it
NOISE_PEAK_TOP = 0.45               # no summit this strong = flat broadband rush, not a voice
SILENCE_STANDDOWN = 3               # bible §22: silence three turns running -> stand down

_HANN = tuple(0.5 - 0.5 * math.cos(2 * math.pi * i / (FRAME_SAMPLES - 1)) for i in range(FRAME_SAMPLES))
_TRIG = tuple(
    (tuple(math.cos(2 * math.pi * f * i / voicefix.RATE) for i in range(FRAME_SAMPLES)),
     tuple(-math.sin(2 * math.pi * f * i / voicefix.RATE) for i in range(FRAME_SAMPLES)))
    for f in SPECTRAL_CENTERS
)


def _unit(vector: list) -> list:
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def cosine(a: list, b: list) -> float:
    """Cosine of two unit vectors — the recognizer's whole comparison."""
    return sum(x * y for x, y in zip(a, b))


def spectral_embedding(pcm_bytes: bytes) -> list:
    """Deterministic in-code voice vector: Hann 30ms frames, 20Hz grid of Goertzel
    magnitudes, per-frame normalized votes accumulated, L2-normalized. A stable
    voice carrier votes the same way every frame; drift moves votes smoothly."""
    samples = array("h")
    samples.frombytes(pcm_bytes)
    votes = [0.0] * len(SPECTRAL_CENTERS)
    for off in range(0, len(samples) - FRAME_SAMPLES + 1, FRAME_SAMPLES):
        frame = samples[off:off + FRAME_SAMPLES]
        rms = math.sqrt(sum(x * x for x in frame) / len(frame))
        if rms < EMBED_MIN_RMS:
            continue
        mags = []
        for cosrow, sinrow in _TRIG:
            re = sum(x * h * c for x, h, c in zip(frame, _HANN, cosrow))
            im = sum(x * h * s for x, h, s in zip(frame, _HANN, sinrow))
            mags.append(math.hypot(re, im))
        total = sum(mags) or 1.0
        for i, mag in enumerate(mags):
            votes[i] += mag / total
    return _unit(votes)


def _spectral_peaks(pcm_bytes: bytes) -> list:
    """Local maxima of the utterance spectrum, strongest first: [(index, magnitude)]."""
    vector = spectral_embedding(pcm_bytes)
    peaks = [i for i in range(1, len(vector) - 1) if vector[i] > vector[i - 1] and vector[i] >= vector[i + 1]]
    peaks.sort(key=lambda i: -vector[i])
    return [(i, vector[i]) for i in peaks], vector


def detect_two_voices(pcm_bytes: bytes) -> bool:
    """Two SHARP spectral summits of comparable strength = two speakers overlapping
    (§22). A noisy plateau is excluded first — broadband rush has many comparable
    'summits' and belongs to the noise row, not the two-voices row."""
    peaks, vector = _spectral_peaks(pcm_bytes)
    if max(vector) < TWO_VOICE_PEAK_TOP:
        return False  # flat audio is never a duet — let the noise/silence rows take it
    return len(peaks) >= 2 and peaks[1][1] >= TWO_VOICE_MIN_SECOND_RATIO * peaks[0][1]


def detect_noise(pcm_bytes: bytes) -> bool:
    """Audible loudness with NO dominant summit = a rush of broadband noise, not speech."""
    loudest = 0.0
    for off in range(0, len(pcm_bytes) - 2 * FRAME_SAMPLES + 1, 2 * FRAME_SAMPLES):
        loudest = max(loudest, frame_rms(pcm_bytes[off:off + 2 * FRAME_SAMPLES]))
    if loudest < RMS_THRESHOLD:
        return False  # quiet audio is the silence path, not the noise path
    _peaks, vector = _spectral_peaks(pcm_bytes)
    return max(vector) < NOISE_PEAK_TOP


def classify(score, threshold, band_floor) -> str:
    """ACCEPT >= threshold; BORDERLINE in the declared band below it; below = REJECT."""
    if score is None or threshold is None:
        return "reject"  # unknown profile space: iron rule — enrollment or privacy
    if score >= threshold:
        return "accept"
    if band_floor is not None and score >= band_floor:
        return "borderline"
    return "reject"


class ResemblyzerScorer:
    """Real speaker-embedding path (resemblyzer, ~35MB, cpu) — nt-guarded, lazy.
    Staged by the M-1 pip table on the AiO; the sandbox proves fixtures instead."""

    def __init__(self):
        self._encoder = None
        self.calls = 0

    def load(self) -> bool:
        if self._encoder is not None:
            return True
        import os
        if os.name != "nt":
            return False  # canon: the recognizer's real weights live on the AiO (M-1), never in a sandbox
        try:
            from resemblyzer import VoiceEncoder
        except ImportError:
            return False  # canon: dependency is M-1 staged; absent here, honestly unavailable
        self._encoder = VoiceEncoder()
        return True

    def embed(self, pcm_bytes: bytes) -> list:
        import numpy as np  # nt-path: resemblyzer's math stack, staged next to it
        self.calls += 1
        wav = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        return [float(v) for v in self._encoder.embed_utterance(wav)]

    def score(self, vector: list, profile: list) -> float:
        return cosine(vector, profile)


class FixtureScorer:
    """The sandbox recognizer: deterministic spectral vectors (declared grid; a
    cold day = the tests' declared Hz drift). calls counted so lock-bypass is provable."""

    def __init__(self):
        self.calls = 0

    def load(self) -> bool:
        return True  # nothing to warm up: the fixture carries no weights

    def embed(self, pcm_bytes: bytes) -> list:
        self.calls += 1
        return spectral_embedding(pcm_bytes)

    def score(self, vector: list, profile: list) -> float:
        return cosine(vector, profile)


def normalize_passphrase(text: str) -> str:
    return " ".join(str(text).lower().split())


def hash_passphrase(text: str, salt: str) -> str:
    """salt:sha256 only — the raw passphrase is never stored, never logged, never persisted."""
    return hashlib.sha256(f"{salt}:{normalize_passphrase(text)}".encode("utf-8")).hexdigest()


class ProfileStore:
    """profiles.json — the Member Files (bible §22/§31): name, relationship, tier,
    embedding, sample hashes, enrollment date (+ passphrase hash for whoever set one).
    Fully local; atomic writes; a corrupt file recovers empty with a logged line."""

    def __init__(self, path, log):
        self._path = Path(path)
        self._log = log
        self._data = self._load()

    def _load(self) -> dict:
        if not self._path.exists():
            return {"version": 1, "members": []}
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            members = data.get("members")
            if not isinstance(members, list):
                raise ValueError("members missing")
            return {"version": 1, "members": members}
        except (ValueError, json.JSONDecodeError):
            self._log.entry("corrupt", cause="profiles.json unreadable — recovered empty, enrollment re-runnable")
            return {"version": 1, "members": []}

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self._data, indent=1), encoding="utf-8")
        tmp.replace(self._path)  # atomic: a reader never sees a torn Member File

    def members_full(self) -> list:
        return list(self._data["members"])

    def add(self, member: dict) -> None:
        self._data["members"].append(member)
        self.save()

    def wipe(self) -> None:
        """Part IX Handover: the Member File back to factory-empty — atomically, unrecoverably."""
        self._data = {"members": []}
        self.save()

    def refresh(self) -> None:
        """Re-read from disk — another seam (enrollment) may have written since construction."""
        self._data = self._load()

    def pass_credentials(self):
        for member in self._data["members"]:
            if member.get("passHash") and member.get("passSalt"):
                return member["passSalt"], member["passHash"]
        return None


class VoiceGate:
    """The recognizer's session brain: threshold/band from enrollment calibration
    (vault kv), session lock + fail streak, silence streak, passphrase restore.
    Every side-effect flows through the state machine's set_audience — never a
    direct mutation of dialog, persona, or vault memory."""

    THRESHOLD_KEY = "voiceid:threshold"
    BAND_KEY = "voiceid:band_floor"
    FAILS_KEY = "voiceid:fails"
    LOCK_KEY = "voiceid:lock"
    SILENCE_KEY = "voiceid:silence"

    def __init__(self, store: ProfileStore, scorer, vault, log):
        self._store = store
        self._scorer = scorer
        self._vault = vault
        self._log = log

    def _threshold(self):
        raw = self._vault.kv_get(self.THRESHOLD_KEY)
        return float(raw) if raw is not None else None

    def _band_floor(self):
        raw = self._vault.kv_get(self.BAND_KEY)
        return float(raw) if raw is not None else None

    def _fails(self) -> int:
        return int(self._vault.kv_get(self.FAILS_KEY) or 0)

    def locked(self) -> bool:
        return self._vault.kv_get(self.LOCK_KEY) == "1"

    def note_silence(self) -> int:
        streak = int(self._vault.kv_get(self.SILENCE_KEY) or 0) + 1
        self._vault.kv_set(self.SILENCE_KEY, str(streak))
        return streak

    def reset_silence(self) -> None:
        self._vault.kv_set(self.SILENCE_KEY, "0")

    def identify(self, pcm_bytes: bytes) -> dict:
        """Score the utterance against every Member File. A locked session never even
        embeds (provable via scorer.calls) — it sits pinned at guest until a pass lands."""
        if self.locked():
            return {"band": "locked", "member": None, "score": None, "suspected_replay": False}
        vector = self._scorer.embed(pcm_bytes)
        best, best_score = None, -1.0
        for member in self._store.members_full():
            score = self._scorer.score(vector, member["embedding"])
            if score > best_score:
                best, best_score = member, score
        band = classify(best_score if best else None, self._threshold(), self._band_floor())
        suspected = (best is not None
                     and hashlib.sha256(pcm_bytes).hexdigest() in best.get("sampleHashes", []))
        return {"band": band, "member": best, "score": best_score if best else None,
                "suspected_replay": suspected}

    def apply(self, result: dict, machine, dialog) -> dict:
        """The matrix's side-effect arm. ACCEPT: unlock, clear fails, tier the room —
        "Cooper." only when Tier-1 actually ARRIVES (no per-turn spam). REJECT and
        BORDERLINE: fail streak, lock at three, guest pinning, the row's byte-exact
        line. LOCKED: quiet guest pinning, no line. All transitions via state.py."""
        band = result["band"]
        if band == "accept":
            tier = result["member"]["tier"]
            self._vault.kv_set(self.LOCK_KEY, "0")
            self._vault.kv_set(self.FAILS_KEY, "0")
            if result["suspected_replay"]:
                # Row "recording-attack": honestly NO special line — convenience-grade
                # detection is unreliable by bible decree; the confirm layers protect.
                self._log.entry("cooperid",
                                note="exact-replay suspected; no line spoken — confirm layers remain the protection")
            if machine.audience != tier:
                machine.set_audience(tier)
                if tier == "cooper":
                    machine.heard()
                    dialog.emit_line(canon.LINE_VERIFIED)
            return {"continue": True, "band": "accept", "locked": False}
        if band == "locked":
            if machine.audience != "guest":
                machine.set_audience("guest")
            return {"continue": True, "band": "locked", "locked": True}
        fails = self._fails() + 1
        self._vault.kv_set(self.FAILS_KEY, str(fails))
        locked_now = fails >= 3
        if locked_now:
            self._vault.kv_set(self.LOCK_KEY, "1")
            self._log.entry("cooperid", note="three recognition failures — session locked to guest")
        if machine.audience != "guest":
            machine.set_audience("guest")
        line = canon.LINE_VOICE_UNCERTAIN if band == "borderline" else canon.LINE_GUEST
        machine.heard()
        dialog.emit_line(line)
        return {"continue": True, "band": band, "locked": locked_now}

    def try_passphrase(self, text, machine) -> bool:
        """Spoken OR typed: one verifier, one rank. A correct pass restores Tier-1
        from ANY lock state — even mid-lock. Already-Cooper = no-op, never a replay."""
        if machine.audience == "cooper":
            return False
        credentials = self._store.pass_credentials()
        if credentials is None:
            return False
        salt, expected = credentials
        if hash_passphrase(text, salt) != expected:
            return False
        self._vault.kv_set(self.LOCK_KEY, "0")
        self._vault.kv_set(self.FAILS_KEY, "0")
        machine.set_audience("cooper")
        self._log.entry("cooperid", note="passphrase accepted: Tier-1 restored (spoken and typed rank alike)")
        return True


def run_recognized_turn(capture, ladder: EarLadder, gate: VoiceGate, machine, bus, dialog, mouth=None) -> dict:
    """The identified voice turn: mic law from capture.py, then the §22 gates in
    bible order — two-voices, noise, silence streak — then recognition BEFORE any
    transcript is routed. Every refusal is a canon line, persisted, never a guess."""
    if mouth is not None:
        mouth.interrupt()
    if machine.state == "armed":
        machine.voice_start()
    if machine.state != "listening":
        return {"ok": False, "line": canon.LINE_CATCH_ALL}
    frames = []
    opened = False
    denied = False
    try:
        opened = capture.open()
    except PermissionError:
        denied = True
    if opened:
        try:
            for frame in capture.frames():
                frames.append(frame)
        finally:
            capture.close()  # mic goes cold on ANY exit path — law, not habit
    if machine.state != "listening":
        return {"ok": False, "line": canon.LINE_CATCH_ALL}  # kill mid-capture: the turn dies with the machine (Law 5)
    if denied:
        machine.heard()
        dialog.emit_line(canon.LINE_MIC_DENIED)  # §22: permission refused at the OS
        return {"ok": False, "line": canon.LINE_MIC_DENIED}
    if not opened:
        machine.heard()
        dialog.emit_line(canon.LINE_NO_MIC)
        return {"ok": False, "line": canon.LINE_NO_MIC}
    pcm = b"".join(frames)
    if detect_two_voices(pcm):
        machine.heard()
        dialog.emit_line(canon.LINE_TWO_VOICES)
        return {"ok": False, "line": canon.LINE_TWO_VOICES}
    if detect_noise(pcm):
        machine.heard()
        dialog.emit_line(canon.LINE_NOISE)
        return {"ok": False, "line": canon.LINE_NOISE}
    spans = vad_spans(pcm)
    if not spans:
        if gate.note_silence() >= SILENCE_STANDDOWN:
            gate.reset_silence()
            machine.heard()
            dialog.emit_line(canon.LINE_EXIT)
            machine.stand_down("silence x3")  # §22 row: silence three turns running stands TARS down
            return {"ok": False, "line": canon.LINE_EXIT, "stood_down": True}
        machine.heard()
        dialog.emit_line(canon.LINE_HEARD_BADLY)
        return {"ok": False, "line": canon.LINE_HEARD_BADLY}
    gate.reset_silence()  # speech reached the recognizer: the streak is broken
    speech_pcm = b"".join(slice_pcm(pcm, span) for span in spans)
    result = gate.identify(speech_pcm)
    outcome = gate.apply(result, machine, dialog)
    finished = finish_voice_turn(pcm, ladder, machine, bus, dialog, gate=gate)
    finished["band"] = result["band"]
    finished["locked"] = outcome["locked"]
    return finished
