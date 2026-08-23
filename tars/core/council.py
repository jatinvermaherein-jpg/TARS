"""The Council (bible §23, P-CORE-12) — parliament, on command: the models compete,
the replies name every seat, and TARS's own verdict says which to trust and why.

THE SEAT PLAN — the standing LANE_MODELS council map, declared here as the source of
truth (router.py imports it; the bytes of the plan never moved): three seats in
parallel on SEPARATE ring keys — fast on groq, smart on groq, council on openrouter.
PARALLELISM + KEY SEPARATION ARE ROUTER LAW (its lock + per-provider cursors); this
module owns the SEATING TRUTH: presentation and verdict.

THE VERDICT BASIS (declared, deterministic — never a coin flip):
  1. agreement count first: every seat's answer byte-compared;
  2. a majority pair wins and is NAMED by seat number;
  3. full disagreement -> SEAT_WEIGHT lane strength (smart > council > fast —
     the heavyweight instruct seat carries the most weight; the free-tier council seat
     sits above the light fast seat);
  4. a seat that never answered (spent or failed key) is announced in place —
     "couldn't make it" — and the verdict composes gracefully from the survivors.
THE QUOTA FLAG rides first (council_note): the count is the number of seats that
ACTUALLY answered — those are the ledgered ones (a failed seat spends nothing),
so the flag line always says what the turn truly cost (§23's 2-3x honesty).
"""
from tars.core import canon
from tars.core.gauge import council_note

COUNCIL_PLAN = (("fast", "groq"), ("smart", "groq"), ("council", "openrouter"))  # (lane, provider)
SEAT_WEIGHT = {"smart": 3, "council": 2, "fast": 1}  # verdict basis #3, declared


def verdict(votes: list) -> str:
    """The deterministic verdict over vote dicts (each: ok, text, lane, ...)."""
    answered = [(i, v) for i, v in enumerate(votes) if v["ok"]]
    if not answered:
        return canon.council_verdict_none()
    if len(answered) == 1:
        return canon.council_verdict_lone(answered[0][0] + 1)
    if len({v["text"] for _i, v in answered}) == 1:  # every answering seat agrees
        if len(answered) == len(votes):
            return canon.council_verdict_unanimous()
        absent = next(i for i, v in enumerate(votes) if not v["ok"])
        return canon.council_verdict_absent(absent + 1, True, "")
    for a in range(len(votes)):  # a majority pair, first found in plan order
        for b in range(a + 1, len(votes)):
            if votes[a]["ok"] and votes[b]["ok"] and votes[a]["text"] == votes[b]["text"]:
                return canon.council_verdict_majority(a + 1, b + 1)
    strongest = max((v for _i, v in answered), key=lambda v: SEAT_WEIGHT[v["lane"]])
    if len(answered) == len(votes):
        return canon.council_verdict_split(strongest["lane"])
    absent = next(i for i, v in enumerate(votes) if not v["ok"])
    return canon.council_verdict_absent(absent + 1, False, strongest["lane"])


def compose(votes: list) -> str:
    """The seat-by-seat presentation + the verdict (router attaches the quota note first
    via note_of; seat names are their honest lane names — [fast], [smart], [council])."""
    lines = [note_of(votes)]
    for i, vote in enumerate(votes):
        seat = canon.number_words(i + 1)
        if vote["ok"]:
            lines.append(f"seat {seat} [{vote['lane']}]: {vote['text']}")
        else:
            lines.append(f"seat {seat} [{vote['lane']}]: couldn't make it.")
    lines.append(verdict(votes))
    return "\n".join(lines)


def note_of(votes: list) -> str:
    """The §23 quota flag: the honest count — seats that answered (and so ledgered)."""
    return council_note(sum(1 for v in votes if v["ok"]))
