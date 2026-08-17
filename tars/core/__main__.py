"""python -m tars.core --demochat — the headless P-CORE-0 proof run.

Replays the contract §6 demo through the real pipeline minus UI: summon, boot
line, a live dial move, a LOCAL-hue status exchange, a red-verb gate answered
with a cancel, and stand-down — every transition on stdout with timestamps.
"""
import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from tars.core import canon
from tars.core.bus import Bus
from tars.core.logx import LogX
from tars.core.settings import Settings
from tars.core.state import OFF, Machine
from tars.core.vault import Vault

_PROCESS_START = time.monotonic()


class Printer:
    """Renders every bridge event as one timestamped stdout line."""

    def __init__(self, out):
        self._out = out
        self._last_state = OFF  # Law 3: TARS always boots OFF, so the first render is a true transition

    def __call__(self, event_type: str, detail: dict) -> None:
        stamp = datetime.now().isoformat(timespec="milliseconds")[11:]
        print(f"[{stamp}] {self._render(event_type, detail)}", file=self._out)

    def _render(self, event_type: str, detail: dict) -> str:
        if event_type == "state":
            dials = detail.get("dials", {})
            previous = self._last_state
            self._last_state = detail.get("state")
            return (
                f"state {previous} -> {detail.get('state')} | dials h={dials.get('humor')} "
                f"v={dials.get('vernacular')} d={dials.get('discretion')} t={dials.get('trust')} | "
                f"audience={detail.get('audience')} lane={detail.get('lane') or '-'} hue={detail.get('hue')}"
            )
        if event_type == "chunk":
            return f"chunk #{detail.get('seq')} {detail.get('text')}"
        if event_type == "done":
            return f"done chat={detail.get('chatId')} hue={detail.get('hue')} lane={detail.get('lane') or '-'}"
        if event_type == "action":
            return (
                f"action {detail.get('kind')} id={detail.get('actionId')} :: "
                f"{detail.get('summary')} -> {detail.get('target')} (gate: typed YES or cancel)"
            )
        if event_type == "transcript":
            return f"transcript {detail.get('who')}> {detail.get('text')}"
        if event_type == "gauge":
            return f"gauge key#{detail.get('keyIndex')} {detail.get('lane')} {detail.get('remainingPct')}%"
        if event_type == "error":
            return f"error [{detail.get('code')}] {detail.get('line')}"
        return f"close :: {detail.get('reason', 'stand down')}"


def run_demochat(data_dir: Path, out) -> int:
    """Run the full demo once against data_dir; returns 0 on clean completion."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    log = LogX(data_dir / "logs.jsonl")
    settings = Settings.load(data_dir / "settings.json", log)
    vault = Vault(data_dir / "vault.db")
    bus = Bus()
    bus.subscribe(Printer(out))
    machine = Machine(settings, log, bus)
    chat = {"id": "", "seq": 0}

    def speak(text: str, hue: str = "local") -> None:
        machine.reply()
        machine.set_context(None, hue)
        bus.emit("chunk", {"chatId": chat["id"], "seq": chat["seq"], "text": text})
        chat["seq"] += 1
        bus.emit("done", {"chatId": chat["id"], "hue": hue, "lane": None})
        machine.spoken()

    def ask(user_text: str, answer) -> None:
        print(f"cooper> {user_text}", file=out)
        machine.text()
        speak(answer())

    runs = int(vault.kv_get("demochat_runs") or 0) + 1
    vault.kv_set("demochat_runs", str(runs))
    vault.remember("journal", f"P-CORE-0 demochat session #{runs}")
    chat["id"] = f"demo-{runs}"

    machine.summon()
    machine.set_context(None, "local")
    bus.emit("chunk", {"chatId": chat["id"], "seq": chat["seq"], "text": canon.LINE_BOOT})
    chat["seq"] += 1
    bus.emit("done", {"chatId": chat["id"], "hue": "local", "lane": None})

    def dial_answer() -> str:
        result = settings.set_dial("humor", 60)
        machine.emit_notice()  # dials move live mid-conversation: push a fresh StateNotice
        return result["line"]

    def status_answer() -> str:
        uptime = int(time.monotonic() - _PROCESS_START)
        return (
            f"Uptime {uptime} seconds. Journal entries: {vault.memory_count()}. "
            f"Vault integrity: {vault.integrity()}. Key gauges arrive with the Watcher phase."
        )

    ask("humor 60", dial_answer)
    ask("status", status_answer)

    print("cooper> shutdown", file=out)
    machine.text()
    bus.emit("action", {"actionId": "red-1", "kind": "red-verb", "summary": "shut down the PC", "target": "this PC"})
    print("operator> cancel", file=out)
    speak(canon.LINE_CANCEL)

    print("cooper> stand down", file=out)
    machine.stand_down("spoken")
    bus.emit("chunk", {"chatId": chat["id"], "seq": chat["seq"], "text": canon.LINE_EXIT})
    bus.emit("done", {"chatId": chat["id"], "hue": "local", "lane": None})
    bus.emit("close", {"reason": "stand down"})

    vault.close()
    log.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="tars.core", description="TARS core — headless phase P-CORE-0")
    parser.add_argument("--demochat", action="store_true", help="run the headless demo chat")
    parser.add_argument("--data", default=None, help="data directory (default: TARS_DATA or ~/.tars)")
    args = parser.parse_args()
    if not args.demochat:
        parser.print_help()
        return 2
    data_dir = Path(args.data) if args.data else Path(os.environ.get("TARS_DATA", str(Path.home() / ".tars")))
    return run_demochat(data_dir, sys.stdout)


if __name__ == "__main__":
    sys.exit(main())
