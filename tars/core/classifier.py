"""The pre-send eye gate (bible §19/§31 — the classifier is THE phase).

FrameClassifier protocol (declared, duck-typed like TeleClient):
    classify(frame) -> "public" | "private"
A frame = {"png": bytes, "title": str, "text": str} — the ops-seam capture plus
declared metadata (window title / visible text; sandbox frames are scripted
fixtures with declared metadata).

The LAW (battery-proven in selftest._look_checks): EVERY frame passes
classify() BEFORE any eyes-lane call — a private frame is refused HERE (§31
line 288: "private documents refused at the classifier, not at the cloud"),
zero adapter payloads ever carry its bytes, and it is dropped from the buffer
immediately. HeuristicClassifier is the REAL local gate — pure-stdlib,
deterministic, zero wire by construction. ModelClassifier is the bible's
<100MB local model as an import-guarded optional seam (the psutil/whisper/
telethon posture exactly); absent lib/weights or off-nt it honestly delegates
to the heuristic and says so via .backend. The classifier is LOCAL by Law —
no implementation in this file may touch the network or take a dependency.
"""
import os
import re

# Closed private-marker list, declared in code (canon comment): fixture-grade rules until
# the <100MB model earns its seat at M-era. Matching is alnum-boundary aware — same doctrine
# as the §34 scanner: a marker glued inside a longer word never fires ("embankment" never
# hits "bank"; "Enter your OTP" always hits "otp").
PRIVATE_MARKERS = (
    "otp", "one time password", "one-time password", "password", "passwd", "pin code",
    "upi pin", "cvv", "card number", "expiry date",
    "bank", "netbanking", "internet banking", "account number", "ifsc",
    "aadhaar", "aadhar", "pan card", "voter id",
    "incognito", "inprivate", "private window", "private browsing",
)


def is_private_text(haystack: str) -> bool:
    """One scan site for title+text: padded, lowercase, boundary-checked."""
    padded = f" {' '.join(str(haystack).lower().split())} "
    for marker in PRIVATE_MARKERS:
        if re.search(rf"(?<![a-z0-9]){re.escape(marker)}(?![a-z0-9])", padded):
            return True
    return False


class HeuristicClassifier:
    """The real local gate: closed marker law over the frame's declared metadata.
    Deterministic, local, zero deps — 'public'/'private', never a confidence guess."""

    def __init__(self):
        self.calls = 0  # battery-proven: calls == frames seen, in every mode

    def classify(self, frame) -> str:
        self.calls += 1
        title = frame.get("title", "") if isinstance(frame, dict) else getattr(frame, "title", "")
        text = frame.get("text", "") if isinstance(frame, dict) else getattr(frame, "text", "")
        return "private" if is_private_text(f"{title} {text}") else "public"


class ModelClassifier:
    """The <100MB local model seam — import-guarded optional. On the AiO with the model
    present it scores with the model; everywhere else it honestly delegates to the
    heuristic gate and reports .backend == 'heuristic'. Zero wire, either way."""

    def __init__(self, weights_path=None, heuristic=None):
        self._delegate = heuristic or HeuristicClassifier()
        self._model = None
        if os.name == "nt" and weights_path:  # canon: the model earns its seat on the AiO only
            try:  # import-guarded presence probe — declared optional surface
                import onnxruntime  # noqa: F401 — a missing lib silently degrades to heuristic
                self._model = None  # model loading lands with the M-era weights (declared pending)
            except ImportError:
                self._model = None

    @property
    def backend(self) -> str:
        return "model" if self._model is not None else "heuristic"

    @property
    def calls(self) -> int:
        return self._delegate.calls

    def classify(self, frame) -> str:
        # The model scores when its M-era weights land (same return contract); until then the
        # heuristic gate carries EVERY frame — declared, honest, battery-proven.
        return self._delegate.classify(frame)
