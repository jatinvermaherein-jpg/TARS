"""The gauge — derives contract §4 StatusReport `keys[]` from the ring.

Declared warn rule (demo-script scene 8: "any <=20% key renders warn-ochre"):
state = "warn" when 0 < remainingPct <= 20 — INCLUSIVE at 20; "spent" at 0;
"ok" otherwise. The router's 80%-budget warn flag uses the same rule.
"""

WARN_REMAINING_PCT = 20


def remaining_pct(key) -> int:
    return max(0, 100 - int(round(key.budget_pct)))


def key_state_word(key) -> str:
    remaining = remaining_pct(key)
    if remaining <= 0:
        return "spent"
    if remaining <= WARN_REMAINING_PCT:
        return "warn"
    return "ok"


def gauge_rows(ring) -> list:
    """Exact contract §4 StatusReport keys[] rows: {index, lane, remainingPct, state}."""
    return [{"index": key.index, "lane": key.pressure_lane(), "remainingPct": remaining_pct(key),
             "state": key_state_word(key)} for key in ring.keys()]


def council_note(count: int) -> str:
    """The honest quota line attached to a council reply (plain text, no emoji)."""
    return f"council of {count} — {count}x quota"
