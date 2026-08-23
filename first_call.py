"""P3.3 — the FIRST LIVE CALL ceremony. One fast-lane ping through the production
ring + real adapters, keys loaded only from C:\\TARS\\secrets.env. This is the first
time TARS's bytes leave the machine — so the card prints the PROOF, never key
material: who served, the reply bytes, tokens ledgered, gauge before/after, latency.

Law: run from PowerShell in the activated venv, repo root. Exit 0 = a live mind
answered. Exit 2 = keys refused (absent/empty secrets.env). Exit 1 = the ring
spoke honestly (all-spent) — courier the card either way, key bytes never.
"""
import os
import sys
import time
from pathlib import Path

from tars.core.adapters import GroqAdapter, OpenRouterAdapter
from tars.core.bus import Bus
from tars.core.gauge import gauge_rows
from tars.core.keys import load_ring, parse_env_file
from tars.core.router import Router
from tars.core.vault import Vault

PING = "Reply with exactly one short line confirming you can hear me."


def _data_dir() -> Path:
    default = Path(r"C:\TARS\data") if os.name == "nt" else Path.home() / ".tars"
    return Path(os.environ.get("TARS_DATA", str(default)))


def _gauge_line(rows) -> str:
    if not rows:
        return "(no keys)"
    return " | ".join(f"key#{row['index']} {row['lane']} {row['remainingPct']}%" for row in rows)


def main() -> int:
    data_dir = _data_dir()
    secrets = data_dir.parent / "secrets.env"
    source = parse_env_file(secrets) if secrets.is_file() else {}
    ring = load_ring(source)
    if not ring.keys():
        print("keys refused — secrets.env absent, empty, or unreadable "
              f"(looked at: {secrets})")  # path only, never contents
        return 2
    vault = Vault(data_dir / "vault.db")
    bus = Bus()
    gauges = []
    bus.subscribe(lambda kind, detail: gauges.append(detail) if kind == "gauge" else None)
    router = Router(ring, {"groq": GroqAdapter(), "openrouter": OpenRouterAdapter()}, vault, bus)

    print("FIRST LIVE CALL — one fast ping through the production ring")
    print(f"gauge before: {_gauge_line(gauge_rows(ring))}")
    started = time.perf_counter()
    try:
        reply = router.route(PING)
    except Exception as exc:  # the wire's own voice — key bytes are never in it
        vault.close()
        print(f"LIVE CALL FAILED ({type(exc).__name__}): {exc}")
        return 1
    latency_ms = int((time.perf_counter() - started) * 1000)

    print(f"gauge after:  {_gauge_line(gauge_rows(ring))}")
    print(f"gauge events pushed: {len(gauges)}")
    print(f"lane: {reply['lane']} · served by: {reply['key_visible_name'] or '(none)'} "
          f"· tokens: {reply['tokens']} · wall: {latency_ms}ms")
    if reply["notices"]:
        print(f"failover notices seen: {len(reply['notices'])} (a key sat out, the ring stepped on)")
    if reply["ok"]:
        print(f"REPLY BYTES: {reply['text']!r}")
        tail = vault.ledger_tail(1)
        if tail:
            print(f"ledger row: lane={tail[0]['lane']} tokens={tail[0]['tokens']}")
        print("FIRST LIVE CALL: GREEN — the wire answers, the ledger counted, the gauge ticked.")
    else:
        print(f"ring answered honestly: {reply['text']}")
    vault.close()
    return 0 if reply["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
