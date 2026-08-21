"""The 8-key quota ring (bible §26 — ring decree frozen at 8: Groq ×6 + OpenRouter ×2).

The loader reads GROQ_KEY_1..6 / OPENROUTER_KEY_1..2 from a mapping the CALLER
provides (host environment or a parsed .env-style file) — it never auto-reads
the environment; real keys never enter a sandbox. Budgets are measured in
requests/day per lane (LANE_CAPS, bible §26); a key is skipped when its lane
counter reaches the cap, and a local-date flip (midnight reset) clears every
counter. Key strings are marked repr=False so they can never leak into a log.
"""
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

SLOT_NAMES = [f"GROQ_KEY_{i}" for i in range(1, 7)] + [f"OPENROUTER_KEY_{i}" for i in range(1, 3)]

LANE_CAPS = {"fast": 14400, "smart": 1000, "eyes": 14400, "ears": 2000, "ultra": 50, "council": 50}
PROVIDER_LANES = {"groq": ("fast", "smart", "eyes", "ears"), "openrouter": ("ultra", "council")}


def parse_env_file(path) -> dict:
    """Parse KEY=VALUE lines from a caller-provided .env-style file (# comments, blanks ignored)."""
    parsed = {}
    for raw in Path(path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        parsed[name.strip()] = value.strip()
    return parsed


@dataclass
class KeyState:
    """One ring slot. First four fields are the contract summary; the rest are book-keeping."""

    provider: str
    index: int
    spent_today: int = 0
    budget_pct: float = 0.0
    lane_seen: list = field(default_factory=list)
    key: str = field(default="", repr=False)  # secret: never rendered, never logged
    failed: bool = False
    lane_spent: dict = field(default_factory=dict, repr=False)

    @property
    def visible_name(self) -> str:
        return f"{self.provider}#{self.index}"

    def spent(self, lane: str) -> int:
        return self.lane_spent.get(lane, 0)

    def healthy_for(self, lane: str) -> bool:
        return (not self.failed) and self.spent(lane) < LANE_CAPS[lane]

    def record(self, lane: str) -> None:
        self.spent_today += 1
        self.lane_spent[lane] = self.spent(lane) + 1
        if lane not in self.lane_seen:
            self.lane_seen.append(lane)
        self.budget_pct = round(max(self.spent(ln) / LANE_CAPS[ln] for ln in PROVIDER_LANES[self.provider]) * 100, 1)

    def pressure_lane(self) -> str:
        """The lane currently driving this key's budget (fresh keys gauge as fast/ultra)."""
        return max(PROVIDER_LANES[self.provider], key=lambda ln: self.spent(ln) / LANE_CAPS[ln])

    def rollover(self) -> None:
        self.spent_today = 0
        self.budget_pct = 0.0
        self.lane_seen = []
        self.failed = False
        self.lane_spent = {}


class Ring:
    """Ordered 8-slot ring with per-provider round-robin cursors and midnight rollover."""

    def __init__(self, keys: list, clock):
        self._keys = sorted(keys, key=lambda k: k.index)
        self._clock = clock
        self._today = clock()
        self._cursors = {}
        for provider in PROVIDER_LANES:
            self._cursors[provider] = 0

    def _roll_if_needed(self) -> None:
        today = self._clock()
        if today != self._today:
            for key in self._keys:
                key.rollover()
            self._today = today

    def keys(self) -> list:
        self._roll_if_needed()
        return list(self._keys)

    def disown(self) -> None:
        """Part IX Handover (keys answered NO at the gate): the live ring lets every key go.
        next_key then finds an empty stable and refuses honestly — no key strings remain."""
        self._keys = []

    def next_key(self, provider: str, lane: str):
        """Next healthy, under-cap key for the lane, walking round-robin. None = drained."""
        self._roll_if_needed()
        candidates = [k for k in self._keys if k.provider == provider]
        if not candidates:
            return None
        start = self._cursors[provider] % len(candidates)
        for step in range(len(candidates)):
            pos = (start + step) % len(candidates)
            if candidates[pos].healthy_for(lane):
                self._cursors[provider] = (pos + 1) % len(candidates)
                return candidates[pos]
        return None


def load_ring(source: dict, clock=None) -> Ring:
    """Build the ring from a caller-provided mapping; missing slots are simply absent."""
    clock = clock or date.today
    states = []
    for name in SLOT_NAMES:
        value = str(source.get(name, "")).strip()
        if not value:
            continue
        slot = int(name.rsplit("_", 1)[1])
        provider, index = ("groq", slot) if name.startswith("GROQ") else ("openrouter", 6 + slot)
        states.append(KeyState(provider=provider, index=index, key=value))
    return Ring(states, clock)
