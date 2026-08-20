"""The 3-gate router (bible §26): fast by default, smart on size/complexity,
ultra and council only when named — voice of the 8-key ring.

Routing gates, in order: "council …" -> council (3 parallel votes on separate
ring keys, 3 ledger entries, quota note attached); "ultra…" -> the OpenRouter
ultra lane; length > LENGTH_THRESHOLD or a complexity keyword -> smart;
otherwise fast. A failed call emits the canon mid-fail line and the walk
continues on the next healthy key; when every key for the lane is spent or
failed, the reply is the canon all-spent line. Every successful call is
ledgered (ts, lane, keyindex, tokens — bible §30) and pushes a gauge event.

Brain calls send [{"role":"system",...}, *history, {"role":"user",...}]: the
persona system prompt (bible §12 clauses verbatim on EVERY call, all three
council seats included) and the rolling chat window thread in from dialog.
Both are optional; omitted they preserve the single-user-message shape.
"""
import threading
from concurrent.futures import ThreadPoolExecutor

from tars.core import canon
from tars.core.gauge import WARN_REMAINING_PCT, council_note, remaining_pct

LANE_MODELS = {
    ("groq", "fast"): "llama-3.1-8b-instant",
    ("groq", "smart"): "llama-3.3-70b-versatile",
    ("groq", "eyes"): "meta-llama/llama-4-scout-17b-16e-instruct",
    ("groq", "ears"): "whisper-large-v3-turbo",
    # bible §26 lane names; the exact :free slugs are confirmed from the OR console at the M-1 key ceremony.
    ("openrouter", "ultra"): "nemotron-3-ultra-550b",
    ("openrouter", "council"): "openrouter-free-council",
}

COMPLEXITY_KEYWORDS = ("explain", "derive", "proof", "why", "solve", "essay",
                       "physics", "chemistry", "maths", "doubt", "concept")  # museum P1 list, field-proven
LENGTH_THRESHOLD = 120  # museum P1: messages longer than 120 chars escalate to smart
COUNCIL_PLAN = (("fast", "groq"), ("smart", "groq"), ("council", "openrouter"))


class Router:
    """One brain ring, three gates, canon failure lines, ledger-every-call."""

    def __init__(self, ring, adapters: dict, vault, bus):
        self._ring = ring
        self._adapters = adapters
        self._vault = vault
        self._bus = bus
        self._lock = threading.Lock()  # serializes ring/reply book-keeping across council threads

    @property
    def ring(self):
        """Read handle for the Watcher's gauge report (P-CORE-9) — reads only, never routes."""
        return self._ring

    def gate(self, text: str) -> str:
        lowered = text.strip().lower()
        if lowered.startswith("council"):
            return "council"
        if lowered.startswith("ultra"):
            return "ultra"
        if len(text) > LENGTH_THRESHOLD or any(word in lowered for word in COMPLEXITY_KEYWORDS):
            return "smart"
        return "fast"

    def route(self, text: str, system_prompt: str = None, history: list = None) -> dict:
        mode = self.gate(text)
        if mode == "council":
            return self._council(text, system_prompt, history)
        return self._single(text, mode, system_prompt, history)

    def route_vision(self, question: str, image_b64: str) -> dict:
        """The eyes lane (bible §19, P-CORE-8): ONE declared message shape — a single user
        message whose content is [text part, base64 data-URL image part]. It reuses
        _single's whole ring/ledger/gauge law with the lane pinned; the classifier has
        already gated the frame before this is ever called (lookd enforces it)."""
        content = [{"type": "text", "text": question},
                   {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}]
        return self._single(content, "eyes")

    def _single(self, text: str, lane: str, system_prompt: str = None, history: list = None) -> dict:
        provider = "openrouter" if lane in ("ultra", "council") else "groq"
        adapter = self._adapters[provider]
        notices = []
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history or [])
        messages.append({"role": "user", "content": text})
        while True:
            with self._lock:
                key = self._ring.next_key(provider, lane)
            if key is None:
                return {"ok": False, "text": canon.LINE_ALL_SPENT, "lane": lane, "key_visible_name": "",
                        "hue": "cloud", "tokens": 0, "notices": notices, "warn": False}
            result = adapter.call(messages, key_string=key.key, key_visible_name=key.visible_name,
                                  model=LANE_MODELS[(provider, lane)])
            if result.ok:
                break
            notices.append(canon.LINE_CLOUD_FAIL)
            with self._lock:
                key.failed = True  # a key that faulted sits out until midnight rollover
        with self._lock:
            key.record(lane)
            self._vault.spend(lane, key.index, result.tokens)
            remaining = remaining_pct(key)
            self._bus.emit("gauge", {"keyIndex": key.index, "lane": lane, "remainingPct": remaining})
        return {"ok": True, "text": result.text, "lane": lane, "key_visible_name": key.visible_name,
                "hue": "cloud", "tokens": result.tokens, "notices": notices,
                "warn": remaining <= WARN_REMAINING_PCT}

    def _council(self, text: str, system_prompt: str = None, history: list = None) -> dict:
        with ThreadPoolExecutor(max_workers=len(COUNCIL_PLAN), thread_name_prefix="tars-council") as pool:
            votes = list(pool.map(lambda spec: self._single(text, spec[0], system_prompt, history), COUNCIL_PLAN))
        notices = []
        for vote in votes:
            notices.extend(vote["notices"])
        lines = [council_note(len(votes))]
        for vote in votes:
            lines.append(f"[{vote['lane']}] {vote['text']}")
        return {"ok": any(vote["ok"] for vote in votes), "text": "\n".join(lines), "lane": "council",
                "key_visible_name": "multiple", "hue": "cloud",
                "tokens": sum(vote["tokens"] for vote in votes), "notices": notices,
                "warn": any(vote["warn"] for vote in votes), "note": council_note(len(votes)), "votes": votes}
