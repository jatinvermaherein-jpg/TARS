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

NAMED SUMMONS (P-CORE-12): the giant and the parliament answer NAME-ONLY, at
word boundaries — "ultra" / "use ultra …" / "ask the giant …" summon ultra,
"council …" summons the council; an unmatched look-alike ("ultraviolet") is a
plain question, never a summon. council.py owns the seat plan, the seating
presentation and the verdict — the router only drives, per its own law.
"""
import threading
from concurrent.futures import ThreadPoolExecutor

from tars.core import canon
from tars.core.council import COUNCIL_PLAN, compose, note_of  # COUNCIL_PLAN: re-export
from tars.core.gauge import WARN_REMAINING_PCT, remaining_pct

# Groq retired llama-3.1-8b-instant and llama-3.3-70b-versatile on 2026-08-16 with
# llama-4-scout already on the deprecation list (console.groq.com/docs/deprecations);
# the fast-lane 404 in the P3.3a doctor run was exactly that retirement, one week on.
# Slugs below are Groq's own recommended replacements; the eyes pick is the current
# vision-capable Groq model (qwen3.6-27b — preview tier, honest risk, catalog-verified
# by key_doctor's roster probe).
LANE_MODELS = {
    ("groq", "fast"): "openai/gpt-oss-20b",
    ("groq", "smart"): "openai/gpt-oss-120b",
    ("groq", "eyes"): "qwen/qwen3.6-27b",
    ("groq", "ears"): "whisper-large-v3-turbo",
    # The OpenRouter seats, pinned against the Aug-2026 free catalog: the ULTRA giant is
    # nemotron-3-ultra 550B; the council's third seat is gemma-4-31b (vendor diversity
    # away from the two groq gpt-oss seats). :free listings ROTATE — if a seat ever
    # answers honestly-spent, the OR console eyeball re-pins the slug.
    ("openrouter", "ultra"): "nvidia/nemotron-3-ultra-550b-a55b:free",
    ("openrouter", "council"): "google/gemma-4-31b-it:free",
}

COMPLEXITY_KEYWORDS = ("explain", "derive", "proof", "why", "solve", "essay",
                       "physics", "chemistry", "maths", "doubt", "concept")  # museum P1 list, field-proven
LENGTH_THRESHOLD = 120  # museum P1: messages longer than 120 chars escalate to smart
NAMED_ULTRA = ("ultra", "use ultra", "ask the giant")  # §24: the giant, named only


def is_named_summon(text: str) -> bool:
    """The named-summon law at word boundary (space/colon/end): command.py stage (4)
    and this gate consult THE SAME table — one declaration, zero drift."""
    lowered = " ".join(str(text).strip().lower().split())
    if lowered == "council" or lowered.startswith(("council ", "council:")):
        return True
    return any(lowered == phrase or lowered.startswith((phrase + " ", phrase + ":"))
               for phrase in NAMED_ULTRA)


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
        lowered = " ".join(text.strip().lower().split())
        if lowered == "council" or lowered.startswith(("council ", "council:")):
            return "council"
        if any(lowered == phrase or lowered.startswith((phrase + " ", phrase + ":"))
               for phrase in NAMED_ULTRA):
            return "ultra"
        if len(text) > LENGTH_THRESHOLD or any(word in lowered for word in COMPLEXITY_KEYWORDS):
            return "smart"
        return "fast"

    def route(self, text: str, system_prompt: str = None, history: list = None) -> dict:
        mode = self.gate(text)
        if mode == "council":
            return self._council(text, system_prompt, history)
        return self._single(text, mode, system_prompt, history)

    def route_lane(self, text: str, lane: str, system_prompt: str = None) -> dict:
        """A lane-pinned text call (P-CORE-10): the sleep-cycle consolidation is smart by
        DECREE, not by the gate's length/keyword read. Same ring/ledger/gauge law as any
        lane — _single does all of it, nothing forked."""
        return self._single(text, lane, system_prompt)

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
        """The drive is router law (3 seats parallel, separate keys, ledger-per-seat);
        the PRESENTATION is council.py's (P-CORE-12): seats named, honest absences,
        the declared verdict, the quota flag counting seats that actually answered."""
        with ThreadPoolExecutor(max_workers=len(COUNCIL_PLAN), thread_name_prefix="tars-council") as pool:
            votes = list(pool.map(lambda spec: self._single(text, spec[0], system_prompt, history), COUNCIL_PLAN))
        notices = []
        for vote in votes:
            notices.extend(vote["notices"])
        return {"ok": any(vote["ok"] for vote in votes), "text": compose(votes), "lane": "council",
                "key_visible_name": "multiple", "hue": "cloud",
                "tokens": sum(vote["tokens"] for vote in votes), "notices": notices,
                "warn": any(vote["warn"] for vote in votes), "note": note_of(votes), "votes": votes}
