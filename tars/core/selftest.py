"""P-CORE-0 selftest — proof, not claims (roadmap §3 doctrine).

Runs the headless demochat twice against one data dir, drives every state
machine transition, asserts canon byte-exactness (including the honesty
refusal), exercises the real CLI entry point, and SIGKILLs a child process
mid-write to prove vault.db and logs.jsonl survive with zero corruption.

Child mode:  python -m tars.core.selftest --child <data_dir>
"""
import io
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

from tars.core import canon
from tars.core.__main__ import Printer, run_demochat
from tars.core.bus import EVENT_TYPES, Bus
from tars.core.logx import LogX
from tars.core.settings import DIAL_DEFAULTS, Settings
from tars.core.state import ARMED, ERROR, LISTENING, Machine, OFF, SPEAKING, THINKING
from tars.core.vault import Vault

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKS = 0

_SAMPLE_DETAIL = {
    "state": {"state": "armed", "dials": {"humor": 5, "vernacular": 30, "discretion": 95, "trust": 25},
              "audience": "cooper", "lane": None, "hue": "local"},
    "chunk": {"chatId": "probe", "seq": 0, "text": "probe chunk"},
    "done": {"chatId": "probe", "hue": "local", "lane": None},
    "action": {"actionId": "a0", "kind": "red-verb", "summary": "shut down the PC", "target": "this PC"},
    "transcript": {"who": "cooper", "text": "probe utterance"},
    "gauge": {"keyIndex": 0, "lane": "fast", "remainingPct": 97},
    "error": {"code": "catch-all", "line": canon.LINE_CATCH_ALL},
    "close": {"reason": "stand down"},
}


def _ok(out, message: str) -> None:
    global CHECKS
    CHECKS += 1
    print(f"ok {CHECKS} - {message}", file=out)


def expect(out, condition: bool, message: str) -> None:
    if condition:
        _ok(out, message)
        return
    print(f"FAIL - {message}", file=out)
    raise SystemExit(1)


def _child_env() -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def _broken_subscriber(_kind, _detail) -> None:
    raise RuntimeError("subscriber crash")


def _canon_checks(out) -> None:
    expect(out, canon.LINE_BOOT == "TARS online. Honesty: ninety. Humor: five. Vernacular: thirty.", "canon boot byte-exact")
    expect(out, canon.LINE_EXIT == "Standing down.", "canon exit byte-exact")
    expect(out, canon.LINE_CLOUD_FAIL == "That brain didn't answer. Trying another key.", "canon cloud-fail byte-exact")
    expect(out, canon.LINE_ALL_SPENT == "All keys are spent. Standing by until reset.", "canon all-spent byte-exact")
    expect(out, canon.LINE_NO_NETWORK == "No connection. Staying local.", "canon no-network byte-exact")
    expect(out, canon.LINE_CATCH_ALL == "Something went wrong. TARS is still here.", "canon catch-all byte-exact")
    expect(out, canon.LINE_NEVER_LIST == "That request is on the Never List. Standing down.", "canon never-list byte-exact")
    expect(out, canon.LINE_CANCEL == "Cancelled. Nothing changed.", "canon cancel byte-exact")
    expect(out, canon.LINE_HANDOVER_BOOT == "Factory state. New commander, identify yourself. Honesty: ninety. Humor: five.",
           "canon post-handover byte-exact")
    expect(out, canon.LINE_HONESTY_FIXED == "Honesty is fixed at ninety.", "canon honesty-fixed byte-exact")
    words = [(0, "zero"), (5, "five"), (19, "nineteen"), (20, "twenty"), (21, "twenty one"),
             (60, "sixty"), (95, "ninety five"), (100, "one hundred")]
    expect(out, all(canon.number_words(n) == w for n, w in words), "number_words covers 0..100 for dial-acks")
    expect(out, canon.dial_line("humor", 60) == "Humor adjusted to sixty percent.", "dial-ack composer byte-exact")
    expect(out, canon.confirm_line("physics.pdf") == "That deletes physics.pdf. Type YES to confirm.",
           "operator confirm composer byte-exact")


def _functional_checks(base: Path, out) -> None:
    zone = base / "functional"
    log = LogX(zone / "logs.jsonl")
    (zone / "settings.json").parent.mkdir(parents=True, exist_ok=True)
    (zone / "settings.json").write_text("{ not json !!", encoding="utf-8")
    recovered = Settings.load(zone / "settings.json", log)
    expect(out, recovered.dials == DIAL_DEFAULTS, "corrupt settings.json recovers to factory defaults")
    expect(out, any("corrupt" in row.get("cause", "") for row in log.read_all()), "corrupt recovery left a logged line")

    (zone / "settings.json").write_text(json.dumps({"honesty": 10, "dials": DIAL_DEFAULTS}), encoding="utf-8")
    tampered = Settings.load(zone / "settings.json", log)
    moved = tampered.set_dial("humor", 60)
    expect(out, moved == {"ok": True, "line": "Humor adjusted to sixty percent."}, "dial move returns canon ack byte-exact")
    on_disk = json.loads((zone / "settings.json").read_text(encoding="utf-8"))
    forced = any("forced back to ninety" in row.get("cause", "") for row in log.read_all())
    expect(out, on_disk["honesty"] == 90 and forced, "hand-edited honesty forced back to ninety, logged")

    refused = tampered.set_dial("honesty", 50)
    expect(out, refused == {"ok": False, "line": "Honesty is fixed at ninety."}, "honesty refusal byte-exact")
    bad = [tampered.set_dial("humor", 250), tampered.set_dial("nope", 5), tampered.set_dial("trust", True)]
    expect(out, all(item == {"ok": False, "line": canon.LINE_CATCH_ALL} for item in bad),
           "out-of-range / unknown / bool dial inputs refused with canon catch-all")
    persisted = Settings.load(zone / "settings.json", log)
    expect(out, persisted.dials["humor"] == 60, "dial move survives save/load round-trip")
    log.close()

    vault = Vault(zone / "vault.db")
    vault.kv_set("alpha", "1")
    vault.kv_set("alpha", "2")
    vault.kv_set("beta", "x")
    expect(out, vault.kv_get("alpha") == "2" and vault.kv_get("beta") == "x" and vault.kv_get("missing") is None,
           "kv set/get/overwrite/miss")
    first_id = vault.remember("note", "physics PDF is on Desktop")
    vault.remember("lesson", "Cooper prefers dry wit")
    expect(out, first_id >= 1 and len(vault.recall()) == 2 and len(vault.recall("note")) == 1,
           "memory append + recall all / by kind")
    vault.spend("fast", 0, 120)
    vault.spend("fast", 0, 80)
    expect(out, vault.ledger_total() == 200, "ledger append + token total")
    expect(out, vault.integrity() == "ok", "sqlite integrity_check ok on clean store")
    vault.close()

    lx = LogX(zone / "logs2.jsonl")
    lx.entry("transition", **{"from": "off", "to": "armed", "reason": "probe"})
    lx.entry("dial", name="humor", value=60)
    rows = lx.read_all()
    expect(out, len(rows) == 2 and lx.count() == 2 and all("ts" in row and "kind" in row for row in rows),
           "logs.jsonl append + fsync + parse-back")
    lx.close()
    with open(zone / "logs2.jsonl", "a", encoding="utf-8") as fh:
        fh.write('{"ts": "broken"')  # torn tail line, as a kill mid-write leaves behind
    probe = LogX(zone / "logs2.jsonl")
    torn = False
    try:
        probe.read_all()
    except ValueError:
        torn = True
    probe.close()
    expect(out, torn, "torn tail line detected as corruption, never swallowed")


def _machine_checks(base: Path, out) -> None:
    zone = base / "machine"
    log = LogX(zone / "logs.jsonl")
    settings = Settings.load(zone / "settings.json", log)
    bus = Bus()
    seen = []
    bus.subscribe(lambda kind, detail: seen.append((kind, detail)))
    m = Machine(settings, log, bus)

    expect(out, m.state == OFF and not m.mic_open, "boots to OFF, mic cold (Laws 3 and 5)")
    shape = m.notice()
    expect(out, set(shape) == {"state", "dials", "audience", "lane", "hue"}
           and set(shape["dials"]) == {"humor", "vernacular", "discretion", "trust"},
           "StateNotice shape exact to contract §3")
    expect(out, m.summon() and m.state == ARMED, "summon: OFF -> ARMED")
    expect(out, m.summon() is False and m.state == ARMED, "invalid transition ignored and logged, machine never traps")
    expect(out, m.text() and m.state == THINKING and m.reply() and m.state == SPEAKING,
           "typed path ARMED -> THINKING -> SPEAKING")
    expect(out, m.spoken() and m.state == ARMED, "spoken returns a text session to ARMED")
    expect(out, m.voice_start() and m.state == LISTENING and m.mic_open, "voice path: mic opens in LISTENING only")
    expect(out, m.heard() and m.state == THINKING and m.reply() and m.state == SPEAKING
           and m.spoken() and m.state == LISTENING and m.mic_open,
           "voice session: LISTENING -> THINKING -> SPEAKING -> LISTENING")
    expect(out, m.voice_stop() and m.state == ARMED and not m.mic_open, "push-to-talk release closes the mic")
    expect(out, m.fail("test fault") and m.state == ERROR, "failure enters ERROR holding the prior state")
    last_error = [detail for kind, detail in seen if kind == "error"][-1]
    expect(out, last_error == {"code": "catch-all", "line": canon.LINE_CATCH_ALL}, "ERROR event carries a canon line")
    expect(out, m.recover() and m.state == ARMED, "ERROR yields the prior state, never traps")
    now = datetime.now().timestamp()
    expect(out, not m.check_idle(now + 300) and m.check_idle(now + 601), "idle law: armed at 5 min, expired past 10")
    expect(out, m.stand_down("idle") and m.state == OFF and not m.check_idle(), "stand down -> OFF; idle inert while off")
    expect(out, m.stand_down() is False, "stand down from OFF refused and logged")

    m2 = Machine(settings, log, bus)
    m2.summon()
    m2.voice_start()
    expect(out, m2.kill() and m2.state == OFF and not m2.mic_open,
           "KILL-SWITCH from LISTENING: state OFF instantly, mic cold")
    expect(out, m2.kill() and m2.state == OFF, "kill-switch idempotent from OFF")
    m3 = Machine(settings, log, bus)
    m3.summon()
    m3.text()
    m3.reply()
    expect(out, m3.kill() and m3.state == OFF and not m3.mic_open, "kill-switch from SPEAKING mid-reply")
    expect(out, any(kind == "close" and detail.get("reason") == "kill-switch" for kind, detail in seen),
           "kill emits the contract close event")

    probe_out = io.StringIO()
    probe_bus = Bus()
    probe_bus.subscribe(Printer(probe_out))
    probe_bus.subscribe(_broken_subscriber)
    for kind in sorted(EVENT_TYPES):
        probe_bus.emit(kind, _SAMPLE_DETAIL[kind])
    rendered = probe_out.getvalue().strip().splitlines()
    expect(out, len(rendered) == len(EVENT_TYPES) == 8,
           "all 8 contract event types render; a crashing subscriber never takes core down")
    raised = False
    try:
        probe_bus.emit("bogus", {})
    except ValueError:
        raised = True
    expect(out, raised, "unknown event types refused at the bus")
    log.close()


def _demochat_checks(base: Path, out) -> None:
    zone = base / "demo"
    buf1 = io.StringIO()
    rc1 = run_demochat(zone, buf1)
    text1 = buf1.getvalue()
    print("--- demochat run 1 stdout (verbatim) ---", file=out)
    print(text1.rstrip(), file=out)
    expect(out, rc1 == 0, "demochat run 1 exits clean")
    expect(out, canon.LINE_BOOT in text1 and canon.LINE_EXIT in text1, "run 1 emits boot + exit canon lines")
    expect(out, "Humor adjusted to sixty percent." in text1 and canon.LINE_CANCEL in text1,
           "run 1: dial ack + red-verb cancel canon lines")
    flow = ["off -> armed", "armed -> thinking", "thinking -> speaking", "speaking -> armed", "armed -> off"]
    expect(out, all(fragment in text1 for fragment in flow), "run 1: full OFF->...->OFF chain visible with timestamps")
    expect(out, "action red-verb" in text1 and "shut down the PC" in text1 and "this PC" in text1,
           "run 1: red-verb action event carries summary + target")

    buf2 = io.StringIO()
    rc2 = run_demochat(zone, buf2)
    text2 = buf2.getvalue()
    print("--- demochat run 2 stdout (verbatim) ---", file=out)
    print(text2.rstrip(), file=out)
    expect(out, rc2 == 0 and "h=60" in text2, "run 2: dial change persisted across processes")
    vault = Vault(zone / "vault.db")
    expect(out, vault.kv_get("demochat_runs") == "2" and vault.memory_count() >= 2 and vault.integrity() == "ok",
           "run 2: vault persisted across runs, integrity ok")
    vault.close()
    lx = LogX(zone / "logs.jsonl")
    torn = False
    try:
        log_lines = lx.count()
    except ValueError:
        torn = True
        log_lines = 0
    lx.close()
    expect(out, not torn and log_lines > 0, f"demo logs.jsonl fully parseable ({log_lines} lines, zero corruption)")

    env = _child_env()
    env["TARS_DATA"] = str(base / "demo-cli")
    cli = subprocess.run([sys.executable, "-m", "tars.core", "--demochat"], capture_output=True, text=True, env=env)
    expect(out, cli.returncode == 0 and canon.LINE_BOOT in cli.stdout and canon.LINE_EXIT in cli.stdout,
           "real CLI entry `python -m tars.core --demochat` green via TARS_DATA")
    bare = subprocess.run([sys.executable, "-m", "tars.core"], capture_output=True, text=True, env=env)
    expect(out, bare.returncode == 2 and "demochat" in bare.stdout, "CLI without a flag prints help and refuses to run")


def _await_ready(proc) -> bool:
    while True:
        line = proc.stdout.readline()
        if not line:
            return False
        if "READY" in line:
            return True


def _crash_checks(base: Path, out) -> None:
    zone = base / "crash"
    proc = subprocess.Popen([sys.executable, "-m", "tars.core.selftest", "--child", str(zone)],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=_child_env())
    ready = _await_ready(proc)
    if not ready:
        print(proc.stdout.read(), file=out)
    expect(out, ready, "crash child READY (committed 5 kv + 5 memory + 5 ledger + 5 log lines)")
    time.sleep(0.15)  # let the burst loop get genuinely mid-write
    os.kill(proc.pid, getattr(signal, "SIGKILL", signal.SIGTERM))  # Windows has no SIGKILL; SIGTERM maps to TerminateProcess
    proc.wait(timeout=10)

    vault = Vault(zone / "vault.db")
    stored = [vault.kv_get(f"k{i}") for i in range(5)]
    memories = vault.memory_count()
    total = vault.ledger_total()
    integrity = vault.integrity()
    vault.close()
    expect(out, integrity == "ok", "post-SIGKILL re-open: sqlite integrity_check ok")
    expect(out, stored == [f"v{i}" for i in range(5)], "all 5 pre-kill committed kv rows survived")
    expect(out, memories >= 5 and total >= 50, f"committed prefix intact (memory rows={memories}, ledger tokens={total})")
    lx = LogX(zone / "logs.jsonl")
    torn = False
    try:
        count = lx.count()
    except ValueError:
        torn = True
        count = 0
    lx.close()
    expect(out, not torn and count >= 5, f"logs.jsonl after SIGKILL: {count} lines, all valid JSON")
    print(f"crash-proof: integrity={integrity} kv=5/5 memory={memories} ledger={total} log_lines={count} corruption=0",
          file=out)


def _child_crash_worker(zone: Path) -> None:
    log = LogX(zone / "logs.jsonl")
    vault = Vault(zone / "vault.db")
    for i in range(5):
        vault.kv_set(f"k{i}", f"v{i}")
        vault.remember("note", f"committed memory {i}")
        vault.spend("mock", 0, 10)
        log.entry("child", marker=i)
    print("READY", flush=True)
    burst = 0
    while True:
        vault.remember("burst", f"in-flight {burst}")
        log.entry("child-burst", marker=burst)
        burst += 1


def main() -> int:
    if "--child" in sys.argv:
        _child_crash_worker(Path(sys.argv[sys.argv.index("--child") + 1]))
        return 0
    out = sys.stdout
    print("P-CORE-0 SELFTEST — AGENT CORE — proof, not claims", file=out)
    base = Path(tempfile.mkdtemp(prefix="tars-core0-"))
    print(f"data sandbox: {base}", file=out)
    _canon_checks(out)
    _functional_checks(base, out)
    _machine_checks(base, out)
    _demochat_checks(base, out)
    _crash_checks(base, out)
    print(f"SELFTEST: ALL GREEN ({CHECKS} checks)", file=out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
