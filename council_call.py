"""P3.4 — the SUMMONS ceremony: the giant, the parliament, and the eyes speak
live through the production ring + real adapters, keys loaded only from
C:\\TARS\\secrets.env. The card prints PROOF, never key material: which lane,
which seat answered, tokens, wall-time, and the reply bytes.

Law: run from PowerShell in the activated venv, repo root. Exit 0 = every
summons answered. Exit 2 = keys refused (absent/empty secrets.env). Exit 1 =
the ring spoke honestly (a seat spent / the wire's own voice) — courier the
whole card either way, key bytes never. Ears stay M-2 (mic stack + whisper
staging at the voice ritual); this ceremony savors text and vision only.
"""
import base64
import os
import sys
import time
from pathlib import Path

from tars.core.adapters import GroqAdapter, OpenRouterAdapter
from tars.core.bus import Bus
from tars.core.dailyops import png_bytes
from tars.core.gauge import gauge_rows
from tars.core.keys import load_ring, parse_env_file
from tars.core.router import LANE_MODELS, Router
from tars.core.vault import Vault

ULTRA_QUESTION = ("ultra: In one short line — what is the single lesson a "
                  "careful machine should never forget?")
COUNCIL_QUESTION = ("council on this: may a helpful machine ever pretend to "
                    "know something it does not?")
EYES_QUESTION = "This image is one solid color. Name the color in one word."


def _data_dir() -> Path:
    default = Path(r"C:\TARS\data") if os.name == "nt" else Path.home() / ".tars"
    return Path(os.environ.get("TARS_DATA", str(default)))


def _gauge_line(rows) -> str:
    if not rows:
        return "(no keys)"
    return " | ".join(f"key#{row['index']} {row['lane']} {row['remainingPct']}%" for row in rows)


def _print_single(label: str, reply: dict, latency_ms: int) -> bool:
    print(f"{label}: lane {reply['lane']} · served by {reply['key_visible_name'] or '(none)'} "
          f"· tokens {reply['tokens']} · wall {latency_ms}ms")
    if reply["notices"]:
        print(f"  failover notices: {len(reply['notices'])} (a key sat out, the ring stepped on)")
    print(f"  BYTES: {reply['text']!r}")
    return reply["ok"]


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

    print("P3.4 SUMMONS — the giant, the parliament, and the eyes speak live")
    print(f"models: ultra={LANE_MODELS[('openrouter', 'ultra')]} · "
          f"council={LANE_MODELS[('openrouter', 'council')]} · eyes={LANE_MODELS[('groq', 'eyes')]}")
    print(f"gauge before: {_gauge_line(gauge_rows(ring))}")
    all_ok = True

    started = time.perf_counter()
    try:
        ultra = router.route(ULTRA_QUESTION)
    except Exception as exc:  # the wire's own voice — key bytes are never in it
        vault.close()
        print(f"ULTRA FAILED ({type(exc).__name__}): {exc}")
        return 1
    all_ok &= _print_single("[1/3] ULTRA (the giant, by name only)", ultra,
                            int((time.perf_counter() - started) * 1000))

    started = time.perf_counter()
    try:
        council = router.route(COUNCIL_QUESTION)
    except Exception as exc:
        vault.close()
        print(f"COUNCIL FAILED ({type(exc).__name__}): {exc}")
        return 1
    print(f"[2/3] COUNCIL — {council['note']} · tokens {council['tokens']} "
          f"· wall {int((time.perf_counter() - started) * 1000)}ms")
    for i, vote in enumerate(council["votes"]):
        seat = f"  seat {i + 1} [{vote['lane']}]"
        print(f"{seat} ({vote['key_visible_name']}): {vote['text']!r}" if vote["ok"]
              else f"{seat}: couldn't make it.")
    all_ok &= council["ok"]

    red_frame = base64.b64encode(png_bytes(64, 64, b"\xff\x00\x00" * (64 * 64))).decode("ascii")
    started = time.perf_counter()
    try:
        eyes = router.route_vision(EYES_QUESTION, red_frame)
    except Exception as exc:
        vault.close()
        print(f"EYES FAILED ({type(exc).__name__}): {exc}")
        return 1
    all_ok &= _print_single("[3/3] EYES (a solid-red card)", eyes,
                            int((time.perf_counter() - started) * 1000))

    print(f"gauge after: {_gauge_line(gauge_rows(ring))}")
    print(f"gauge events pushed: {len(gauges)} (5 when every summons answers)")
    for row in vault.ledger_tail(5):
        print(f"ledger row: lane={row['lane']} tokens={row['tokens']}")
    vault.close()
    if all_ok:
        print("P3.4 SUMMONS: GREEN — the giant answered, the parliament deliberated, the eyes saw.")
        return 0
    print("P3.4 SUMMONS: the ring spoke honestly (read the seat lines) — courier the whole card.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
