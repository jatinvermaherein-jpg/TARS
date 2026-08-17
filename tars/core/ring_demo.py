"""python -m tars.core.ring_demo — scripted fixture tour of the brain ring.

Fixtures only: every "call" is answered by FixtureAdapter scripts, zero
network. The tour shows a fast call, a keyword escalation to smart, a council
of three with its quota note, then a single-key arc that surfaces the 80%
warn flag and the drained-ring canon line, the gauge table, and the ledger
tail.
"""
import argparse
import os
import sys
from pathlib import Path

from tars.core.adapters import FixtureAdapter
from tars.core.bus import Bus
from tars.core.gauge import gauge_rows
from tars.core.keys import LANE_CAPS, load_ring
from tars.core.router import Router
from tars.core.vault import Vault

MOCK_KEYS = {f"GROQ_KEY_{i}": f"gsk-fixture-{i}" for i in range(1, 7)}
MOCK_KEYS.update({f"OPENROUTER_KEY_{i}": f"or-fixture-{i}" for i in range(1, 3)})


class Tour:
    """Runs the scripted exchanges, collecting gauge events per exchange."""

    def __init__(self, out):
        self._out = out
        self._gauge_events = []

    def collect(self, kind, detail) -> None:
        if kind == "gauge":
            self._gauge_events.append(detail)

    def ask(self, router: Router, user_text: str) -> None:
        out = self._out
        print(f"cooper> {user_text}", file=out)
        reply = router.route(user_text)
        for notice in reply["notices"]:
            print(f"  notice: {notice}", file=out)
        print(f"  gate -> lane={reply['lane']} key={reply['key_visible_name'] or '-'} "
              f"hue={reply['hue']} tokens={reply['tokens']} warn={reply['warn']}", file=out)
        for line in reply["text"].splitlines():
            print(f"  tars> {line}", file=out)
        while self._gauge_events:
            detail = self._gauge_events.pop(0)
            print(f"  event gauge: key#{detail['keyIndex']} {detail['lane']} {detail['remainingPct']}% left", file=out)


def run_ringdemo(data_dir: Path, out) -> int:
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    vault = Vault(data_dir / "vault.db")
    bus = Bus()
    tour = Tour(out)
    bus.subscribe(tour.collect)

    ring = load_ring(MOCK_KEYS)
    router = Router(ring, {
        "groq": FixtureAdapter("groq", [
            ("ok", "Chrome opens on command.", 12),
            ("ok", "The sky is blue because air scatters short wavelengths most.", 31),
            ("ok", "fast vote: finish the worksheet first.", 9),
            ("ok", "smart vote: derive once, drill the steps, then games.", 14),
        ]),
        "openrouter": FixtureAdapter("openrouter", [
            ("ok", "council-spare vote: agree with smart.", 8),
        ]),
    }, vault, bus)

    print("== TARS brain ring — fixture tour (zero network) ==", file=out)
    tour.ask(router, "open Chrome")
    tour.ask(router, "explain why the sky is blue")
    tour.ask(router, "council on this: games before the worksheet?")

    print("== single-key arc: the warn flag, then drained ==", file=out)
    solo_ring = load_ring({"OPENROUTER_KEY_1": "or-fixture-solo"})
    solo_key = solo_ring.next_key("openrouter", "ultra")
    for _ in range(LANE_CAPS["ultra"] - 1):  # walk the key to 49/50 so the next call crosses the warn line
        solo_key.record("ultra")
    unused_groq = FixtureAdapter("groq", [])  # the solo arc only ever gates to ultra
    solo_or = FixtureAdapter("openrouter", [("ok", "ultra lane: the 50th and final answer of the day.", 40)])
    solo = Router(solo_ring, {"groq": unused_groq, "openrouter": solo_or}, vault, bus)
    tour.ask(solo, "ultra: settle the physics debate")
    tour.ask(solo, "ultra: one more")

    print("== gauge (contract §4 keys[] rows, main ring) ==", file=out)
    for row in gauge_rows(ring):
        print(f"  key#{row['index']} {row['lane']:8} {row['remainingPct']:3}% {row['state']}", file=out)
    print(f"ledger total: {vault.ledger_total()} tokens across all lanes", file=out)
    print("== ledger tail ==", file=out)
    for entry in vault.ledger_tail(6):
        print(f"  {entry['ts']} lane={entry['lane']:8} key#{entry['keyindex']} tokens={entry['tokens']}", file=out)
    vault.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="tars.core.ring_demo", description="TARS brain ring — fixture tour")
    parser.add_argument("--data", default=None, help="data directory (default: TARS_DATA or ~/.tars)")
    args = parser.parse_args()
    root = Path(args.data) if args.data else Path(os.environ.get("TARS_DATA", str(Path.home() / ".tars")))
    return run_ringdemo(root / "ring-demo", sys.stdout)


if __name__ == "__main__":
    sys.exit(main())
