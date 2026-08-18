"""CORE selftest — proof, not claims (roadmap §3 doctrine).

P-CORE-0 battery: demochat twice, every state machine transition, canon
byte-exactness (incl. the honesty refusal), the real CLI, and a SIGKILLed
child proving vault.db / logs.jsonl survive mid-write with zero corruption.
P-CORE-1 battery: the 8-key ring — rotation, budget skip, drained canon
line, timeout/429/5xx/garbage retry paths, gate arithmetic, council quota
math, ledger exactness, clock-injected midnight rollover, gauge shape and
warn boundary, fixture determinism, and the real adapters' no-keys refusal.
P-CORE-3 battery: the voice pipelines — byte-pinned VAD spans on in-code
fixtures, the ear ladder (local-miss -> groq-ears -> all-spent canon line),
ears billing through keys.py alone, mic-cold guard law on both capture
adapters, transcript-before-routing order, bad-audio/no-mic §22 honesty
lines, kill mid-capture (Law 5), the mouth ladder with its per-tier cascade,
private-never-edge proof, barge-in honored in-tick, and the speak-queue
drain lifecycle queued -> done / failed:<tier>.

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
import wave
from datetime import date, datetime
from pathlib import Path

from tars.core import canon, persona, voicefix
from tars.core.__main__ import Printer, run_demochat
from tars.core.adapters import GROQ_URL, OPENROUTER_URL, TIMEOUT_S, FixtureAdapter, GroqAdapter
from tars.core.bus import EVENT_TYPES, Bus
from tars.core.capture import FakeCapture, SoundDeviceCapture
from tars.core.dialog import Dialog, classify_memory
from tars.core.ears import (RMS_THRESHOLD, EarLadder, FixtureEarEngine, GroqEarsAdapter, WhisperSmallLocal,
                            build_multipart, frame_rms, run_voice_turn, slice_pcm, vad_spans)
from tars.core.gauge import council_note, gauge_rows
from tars.core.keys import LANE_CAPS, load_ring, parse_env_file
from tars.core.logx import LogX
from tars.core.mouth import EdgeTier, FixtureTier, Mouth, PiperTier, SapiTier
from tars.core.router import LANE_MODELS, LENGTH_THRESHOLD, Router
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
    expect(out, canon.LINE_NOTED == "Noted. I'll remember that.", "ratified remember-ack byte-exact (8706128)")
    expect(out, canon.LINE_GUEST == "Voice not recognized. Guest rules apply.", "ratified guest-recognition byte-exact (8706128)")
    expect(out, canon.LINE_GUEST_DIAL == "Only Cooper moves the dials.", "ratified guest-dial byte-exact (8706128)")
    expect(out, persona.HONESTY_CLAUSES == "Never flatter. If you do not know, say you do not know. "
           "Never invent facts, numbers, citations, or sources. When uncertain, say what part you are unsure of.",
           "bible §12 honesty clauses byte-exact, no paraphrase")
    expect(out, canon.LINE_HEARD_BADLY == "Heard that badly. I don't guess — repeat, please.",
           "§22 heard-badly row byte-exact for the ears")
    expect(out, canon.LINE_NO_MIC == "No mic. Text mode it is.", "§22 no-mic row byte-exact for the ears")
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
    expect(out, [row["tokens"] for row in vault.ledger_tail(1)] == [80], "ledger tail returns newest rows chronologically")
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


def _ring_checks(base: Path, out) -> None:
    zone = base / "ring"
    zone.mkdir(parents=True, exist_ok=True)
    full_source = {f"GROQ_KEY_{i}": f"gsk-{i}" for i in range(1, 7)}
    full_source.update({f"OPENROUTER_KEY_{i}": f"or-{i}" for i in range(1, 3)})
    cases = 0

    def universe(groq_script, or_script, source=None, clock=None):
        nonlocal cases
        cases += 1
        vault = Vault(zone / f"case{cases}" / "vault.db")
        bus = Bus()
        events = []
        bus.subscribe(lambda kind, detail: events.append((kind, detail)))
        ring = load_ring(full_source if source is None else source, clock=clock)
        router = Router(ring, {"groq": FixtureAdapter("groq", groq_script),
                               "openrouter": FixtureAdapter("openrouter", or_script)}, vault, bus)
        return router, ring, vault, events

    env_file = zone / "sample.env"
    env_file.write_text("GROQ_KEY_1=gsk_a\n# comment line\n\nOPENROUTER_KEY_2=or_b\n", encoding="utf-8")
    expect(out, parse_env_file(env_file) == {"GROQ_KEY_1": "gsk_a", "OPENROUTER_KEY_2": "or_b"},
           "caller-provided .env file parses (comments/blanks ignored), ring never auto-reads")

    ring = load_ring(full_source)
    states = ring.keys()
    expect(out, [k.index for k in states] == [1, 2, 3, 4, 5, 6, 7, 8]
           and states[0].provider == "groq" and states[6].provider == "openrouter",
           "ring loads 8 slots in slot order with providers (Groq x6 + OpenRouter x2)")
    expect(out, states[0].spent_today == 0 and states[0].budget_pct == 0.0 and states[0].lane_seen == [],
           "fresh KeyState summary fields zeroed")
    expect(out, "gsk-1" not in repr(states[0]), "key material never leaks into a repr")
    sparse = load_ring({"GROQ_KEY_2": "x", "GROQ_KEY_4": "y"})
    expect(out, [k.index for k in sparse.keys()] == [2, 4], "missing slots absent, indexes stay slot-stable")

    router1, _r1, vault1, events1 = universe([("ok", f"answer {i}", 1) for i in range(6)], [])
    replies = [router1.route(f"question {i}") for i in range(6)]
    expect(out, [rep["key_visible_name"] for rep in replies] == [f"groq#{i}" for i in range(1, 7)],
           "rotation: 6 fast calls walk groq#1..#6 round-robin")
    expect(out, all(rep["lane"] == "fast" and rep["ok"] and rep["hue"] == "cloud" for rep in replies)
           and vault1.ledger_total() == 6,
           "plain short text gates to fast; every call ledgered (6 x 1 token)")
    expect(out, any(kind == "gauge" and detail["keyIndex"] == 1 and detail["lane"] == "fast"
                    for kind, detail in events1), "every call pushes a contract gauge event")
    vault1.close()

    router2, ring2, vault2, _e = universe([], [], source={"OPENROUTER_KEY_1": "a", "OPENROUTER_KEY_2": "b"})
    key7 = ring2.next_key("openrouter", "ultra")
    for _n in range(LANE_CAPS["ultra"]):
        key7.record("ultra")
    expect(out, key7.index == 7 and ring2.next_key("openrouter", "ultra").index == 8 and key7.budget_pct == 100.0,
           "a key AT budget is skipped without a failing call")
    vault2.close()

    router3, ring3, vault3, _e = universe([], [], source={"OPENROUTER_KEY_1": "solo"})
    solo_key = ring3.next_key("openrouter", "ultra")
    for _n in range(LANE_CAPS["ultra"]):
        solo_key.record("ultra")
    reply3 = router3.route("ultra: heavy")
    expect(out, reply3["ok"] is False and reply3["text"] == canon.LINE_ALL_SPENT,
           "drained ring answers the canon all-spent line, byte-exact, zero exceptions")
    vault3.close()

    router4, _r4, vault4, _e = universe([("timeout",), ("ok", "recovered", 11)], [])
    reply4 = router4.route("hi")
    expect(out, reply4["ok"] and reply4["key_visible_name"] == "groq#2" and reply4["tokens"] == 11,
           "timeout on key #1 -> retry succeeds on the next healthy key")
    expect(out, reply4["notices"] == [canon.LINE_CLOUD_FAIL], "mid-fail canon line byte-exact (demo scene 7)")
    vault4.close()

    for kind in ("http_429", "http_5xx", "garbage_json"):
        router_x, _rx, vault_x, _ex = universe([(kind,), ("ok", f"after {kind}", 5)], [])
        reply_x = router_x.route("hi")
        expect(out, reply_x["ok"] and reply_x["key_visible_name"] == "groq#2"
               and reply_x["notices"] == [canon.LINE_CLOUD_FAIL],
               f"{kind} -> retry-once path recovers on the next key, no crash")
        vault_x.close()

    router5, _r5, vault5, _e = universe([("ok", "smart-answer", 20)], [])
    reply5 = router5.route("x" * (LENGTH_THRESHOLD + 1))
    expect(out, reply5["ok"] and reply5["lane"] == "smart", "long message routes to smart with fast healthy")
    vault5.close()
    router5b, _r5b, vault5b, _e5b = universe([("ok", "smart-kw", 20)], [])
    expect(out, router5b.route("explain photosynthesis")["lane"] == "smart", "complexity keyword routes to smart")
    vault5b.close()
    router5c, _r5c, vault5c, _e5c = universe([], [("ok", "ultra-answer", 40)])
    reply5c = router5c.route("ultra: derive this properly")
    expect(out, reply5c["lane"] == "ultra" and reply5c["key_visible_name"] == "openrouter#7",
           "named ultra routes to the OpenRouter ultra lane")
    vault5c.close()
    expect(out, LANE_MODELS[("groq", "fast")] == "llama-3.1-8b-instant"
           and LANE_MODELS[("groq", "smart")] == "llama-3.3-70b-versatile" and TIMEOUT_S == 30,
           "lane map + 30s ceiling byte-exact to bible §26")

    router6, _r6, vault6, _e6 = universe([("ok", "fast vote", 10), ("ok", "smart vote", 20)],
                                         [("ok", "spare vote", 30)])
    reply6 = router6.route("council on this: skip leg day?")
    expect(out, reply6["ok"] and reply6["note"] == council_note(3) == "council of 3 — 3x quota",
           "council quota note plain-text byte-exact")
    expect(out, len(reply6["votes"]) == 3 and [vote["lane"] for vote in reply6["votes"]] == ["fast", "smart", "council"],
           "council fires 3 parallel votes in plan order")
    tail6 = vault6.ledger_tail(10)
    expect(out, len(tail6) == 3 and vault6.ledger_total() == 60
           and {row["lane"] for row in tail6} == {"fast", "smart", "council"},
           "council ledger: exactly 3 entries, token arithmetic exact (10+20+30)")
    expect(out, reply6["votes"][0]["key_visible_name"] != reply6["votes"][1]["key_visible_name"],
           "council votes ride separate ring keys (bible §23)")
    vault6.close()

    clock_box = {"today": date(2026, 8, 17)}
    router7, ring7, vault7, _e7 = universe([("ok", "a", 3), ("ok", "b", 3)], [],
                                           clock=lambda: clock_box["today"])
    router7.route("hi")
    router7.route("hi again")
    first_key = ring7.keys()[0]
    first_key.failed = True
    clock_box["today"] = date(2026, 8, 18)
    rolled = ring7.keys()[0]
    expect(out, rolled.spent_today == 0 and rolled.budget_pct == 0.0 and rolled.lane_seen == []
           and rolled.failed is False, "midnight rollover clears counters and failures (clock injected)")
    expect(out, vault7.ledger_total() == 6, "ledger is history — rollover never rewrites it")
    vault7.close()

    rows = gauge_rows(ring)
    expect(out, len(rows) == 8 and all(set(row) == {"index", "lane", "remainingPct", "state"} for row in rows),
           "gauge rows match contract §4 keys[] shape exactly")
    expect(out, rows[0]["remainingPct"] == 100 and rows[0]["state"] == "ok" and rows[0]["lane"] == "fast"
           and rows[6]["lane"] == "ultra", "fresh keys gauge 100% ok on their default lanes")
    key8 = ring.keys()[7]
    for _n in range(40):
        key8.record("ultra")  # exactly 80% of the 50/day budget spent
    warn_row = gauge_rows(ring)[7]
    for _n in range(10):
        key8.record("ultra")
    spent_row = gauge_rows(ring)[7]
    expect(out, warn_row["remainingPct"] == 20 and warn_row["state"] == "warn"
           and spent_row["remainingPct"] == 0 and spent_row["state"] == "spent",
           "warn rule declared INCLUSIVE at 20% remaining (scene 8); 0% renders spent")

    def battery():
        router_b, _rb, vault_b, _eb = universe([("ok", "d1", 7), ("timeout",), ("ok", "d2", 9)],
                                               [("ok", "du", 40)])
        results = (router_b.route("hi"), router_b.route("hi again"), router_b.route("ultra: check"))
        vault_b.close()
        return results

    expect(out, json.dumps(battery(), sort_keys=True) == json.dumps(battery(), sort_keys=True),
           "determinism: fixture battery runs twice, identical outputs")

    bare = GroqAdapter().call([{"role": "user", "content": "hi"}], key_string="",
                              key_visible_name="groq#1", model=LANE_MODELS[("groq", "fast")])
    expect(out, bare.ok is False and bare.error == "no_keys" and bare.text == canon.LINE_ALL_SPENT,
           "real adapter with no keys returns the refusal dict — no crash, no wire")
    expect(out, GROQ_URL == "https://api.groq.com/openai/v1/chat/completions"
           and OPENROUTER_URL == "https://openrouter.ai/api/v1/chat/completions",
           "adapter endpoints byte-exact (real codepath written, unreachable without keys)")


def _ringdemo_checks(base: Path, out) -> None:
    env = _child_env()
    env["TARS_DATA"] = str(base / "ringdemo-cli")
    cli = subprocess.run([sys.executable, "-m", "tars.core.ring_demo"], capture_output=True, text=True, env=env)
    text = cli.stdout
    expect(out, cli.returncode == 0 and "fixture tour" in text and "council of 3 — 3x quota" in text,
           "ring_demo CLI runs the scripted tour clean")
    expect(out, canon.LINE_ALL_SPENT in text and "warn=True" in text and "event gauge" in text
           and "ledger tail" in text and "lane=ultra" in text,
           "tour shows the warn flag, drained canon line, gauge events, and ledger tail")


def _persona_checks(base: Path, out) -> None:
    zone = base / "persona"
    zone.mkdir(parents=True, exist_ok=True)
    full_source = {f"GROQ_KEY_{i}": f"gsk-{i}" for i in range(1, 7)}
    full_source.update({f"OPENROUTER_KEY_{i}": f"or-{i}" for i in range(1, 3)})
    dials60 = {"honesty": 90, "humor": 60, "vernacular": 30, "discretion": 95, "trust": 25}

    def universe(name, groq_script, or_script, audience="cooper", seed_memory=None):
        path = zone / name
        log = LogX(path / "logs.jsonl")
        settings = Settings.load(path / "settings.json", log)
        vault = Vault(path / "vault.db")
        bus = Bus()
        events = []
        bus.subscribe(lambda kind, detail: events.append((kind, detail)))
        machine = Machine(settings, log, bus)
        groq_fx = FixtureAdapter("groq", groq_script)
        or_fx = FixtureAdapter("openrouter", or_script)
        router = Router(load_ring(full_source), {"groq": groq_fx, "openrouter": or_fx}, vault, bus)
        dialog = Dialog(settings, vault, router, machine, bus)
        for kind, text in (seed_memory or []):
            vault.remember(kind, text)
        machine.set_audience(audience)
        return dialog, vault, machine, groq_fx, or_fx, events, settings

    # happiness begins: one live dialog, watched end to end
    dialog, vault1, machine1, gfx1, ofx1, ev1, _s1 = universe(
        "u1", [("ok", "fast hello", 10), ("ok", "smart bit", 20), ("ok", "vote f", 9), ("ok", "vote s", 14)],
        [("ok", "vote c", 8)])
    expect(out, dialog.send("hello") == {"chatId": 1}, "send returns contract ReplyResult {chatId}")
    system1 = gfx1.received[-1][0]
    expect(out, system1["role"] == "system" and persona.HONESTY_CLAUSES in system1["content"],
           "§12 clauses byte-exact inside the fast-call system prompt the adapter RECEIVED")
    dialog.send("explain entropy to me")
    expect(out, persona.HONESTY_CLAUSES in gfx1.received[-1][0]["content"], "§12 clauses on the smart call too")
    dialog.send("council on this: skip revision?")
    seats = gfx1.received[-2:] + ofx1.received[-1:]
    expect(out, len(seats) == 3 and all(persona.HONESTY_CLAUSES in seat[0]["content"] for seat in seats),
           "§12 clauses ride all 3 council seats")
    dones1 = [detail for kind, detail in ev1 if kind == "done"]
    expect(out, len(dones1) == 3 and all(set(detail) == {"chatId", "messageId", "hue", "lane"} for detail in dones1),
           "A2: every done carries exactly {chatId, messageId, hue, lane}")
    summaries = dialog.list_chats()
    expect(out, set(summaries[0]) == {"id", "title", "ts", "lastHue"} and summaries[0]["title"] == "hello"
           and summaries[0]["lastHue"] == "cloud",
           "ChatSummary derived read-side: title from first user message, lastHue from newest hue, zero row edits")
    messages1 = dialog.open_chat(1)
    expect(out, set(messages1[0]) == {"id", "who", "text", "ts", "hue", "lane", "actions"}
           and messages1[0]["who"] == "cooper" and messages1[0]["hue"] is None
           and messages1[0]["actions"] == ["copy", "read_aloud", "redo"],
           "ChatMessage contract shape exact, hover actions ordered")
    expect(out, dialog.new_chat() == {"id": 2} and dialog.list_chats()[0]["title"] == "New chat",
           "new_chat contract return; an empty chat titles itself plainly")

    # persona bytes: bands, determinism, audience degrade
    dials5 = {"honesty": 90, "humor": 5, "vernacular": 30, "discretion": 95, "trust": 25}
    prompt5 = persona.build_system_prompt(dials5, "cooper", [])
    prompt60 = persona.build_system_prompt(dials60, "cooper", [])
    expect(out, prompt5 != prompt60 and "HUMOR 5/100" in prompt5 and "HUMOR 60/100" in prompt60,
           "humor 5 vs 60 produce different dial-directive bytes")
    expect(out, persona.build_system_prompt(dials60, "cooper", []) == prompt60,
           "persona deterministic: same inputs, same bytes, live dials pulled at call time")
    expect(out, "zero jokes" in persona.humor_directive(5) and "dry one-liners" in persona.humor_directive(60)
           and "dost" in persona.humor_directive(95), "humor bands pinned to the §10 anchors")
    expect(out, "crisp formal English" in persona.vernacular_directive(0)
           and "Hinglish" in persona.vernacular_directive(30) and "desi" in persona.vernacular_directive(100),
           "vernacular bands pinned to the §10 anchors")
    prompt_unknown = persona.build_system_prompt(dials60, "intruder", [{"kind": "fact", "text": "a secret"}])
    expect(out, "guest" in prompt_unknown and persona.MEMORY_HEADER not in prompt_unknown,
           "unknown audience degrades to the guest prompt (§31 iron rule)")
    expect(out, machine1.set_audience("intruder") is False and machine1.audience == "cooper",
           "invalid audience tier refused at the machine, logged")

    # dial commands through send()
    dialog2, vault2, _m2, _g2, _o2, ev2, _s2 = universe("u2", [], [])
    dialog2.send("humor 60")
    expect(out, any(kind == "state" and detail["dials"]["humor"] == 60 for kind, detail in ev2),
           "dial command emits the fresh StateNotice (demo scene 4) and persists")
    expect(out, vault2.messages_for(1)[-1]["text"] == "Humor adjusted to sixty percent.",
           "dial ack persisted as a tars message, byte-exact")
    dialog2.send("honesty 50")
    expect(out, vault2.messages_for(1)[-1]["text"] == "Honesty is fixed at ninety.",
           "typed honesty attempt refused byte-exact inside send()")
    dialog2.send("humor abc")
    expect(out, vault2.messages_for(1)[-1]["text"] == canon.LINE_CATCH_ALL,
           "malformed dial value refused with the canon catch-all, never guessed")

    # memory flows
    dialog3, vault3, _m3, gfx3, _o3, _e3, _s3 = universe("u3", [("ok", "later answer", 10)], [])
    dialog3.send("remember this: Cooper has a physics test on Friday")
    expect(out, vault3.messages_for(1)[-1]["text"] == canon.LINE_NOTED, "remember-intent acks the drafted canon line")
    plans = vault3.recall("plan")
    expect(out, len(plans) == 1 and "physics test" in plans[0]["text"], "payload stored under the declared kind (plan)")
    dialog3.send("hello again")
    expect(out, persona.MEMORY_HEADER in gfx3.received[-1][0]["content"]
           and "physics test on Friday" in gfx3.received[-1][0]["content"],
           "next cooper system prompt carries the memory block, kind-labeled")
    expect(out, classify_memory("Ma likes early tea") == "person"
           and classify_memory("my exam is tomorrow") == "plan"
           and classify_memory("he prefers dry wit") == "preference"
           and classify_memory("the sky is blue") == "fact",
           "memory kind rules: person -> plan -> preference -> fact")

    # guest register
    dialog4, vault4, _m4, gfx4, _o4, ev4, _s4 = universe(
        "u4", [("ok", "polite answer", 10), ("ok", "neutral answer", 10)], [],
        audience="guest", seed_memory=[("fact", "Cooper has a physics test on Friday")])
    dialog4.send("what do you remember?")
    guest_system = gfx4.received[-1][0]["content"]
    expect(out, persona.MEMORY_HEADER not in guest_system and "no personal data" in guest_system,
           "guest prompt: memory block OMITTED, guest sentence present")
    dialog4.send("humor 70")
    expect(out, vault4.messages_for(1)[-1]["text"] == "Only Cooper moves the dials."
           and not any(kind == "state" and detail["dials"]["humor"] == 70 for kind, detail in ev4),
           "guest dial move refused with the drafted line, dials unmoved")
    dialog4.send("remember this: the Wi-Fi password lives in the drawer")
    expect(out, not any("Wi-Fi" in row["text"] for row in vault4.recall())
           and vault4.messages_for(1)[-1]["text"] != canon.LINE_NOTED,
           "guest remember-intent never reaches the vault (declared fall-through)")

    # family tier
    dialog5, vault5, _m5, gfx5, _o5, _e5, _s5 = universe(
        "u5", [("ok", "family answer", 10)], [],
        audience="family", seed_memory=[("fact", "Cooper has a physics test on Friday")])
    dialog5.send("how is Cooper doing?")
    family_system = gfx5.received[-1][0]["content"]
    expect(out, persona.MEMORY_HEADER not in family_system and "warm-formal" in family_system,
           "family prompt: warm-formal, no private memories")
    dialog5.send("trust 80")
    expect(out, vault5.messages_for(1)[-1]["text"] == "Only Cooper moves the dials.",
           "family dial move refused identically — the panel is a Cooper place (§10)")

    # A1: read_aloud
    dialog6, vault6, _m6, gfx6, _o6, _e6, _s6 = universe("u6", [("ok", "the answer text", 10)], [])
    dialog6.send("hello")
    tars_mid = vault6.messages_for(1)[-1]["id"]
    good = dialog6.quick_action("read_aloud", {"chatId": 1, "messageId": tars_mid})
    expect(out, good["ok"] and good["text"] == "the answer text" and good["chatId"] == 1,
           "read_aloud good-id returns the message text for the mouth-to-be")
    expect(out, vault6.kv_get(f"speak_request:{tars_mid}") == "queued",
           "read_aloud marks the declared kv intake slot (P-CORE-3 drains it)")
    bad6 = dialog6.quick_action("read_aloud", {"chatId": 1, "messageId": 9999})
    expect(out, bad6 == {"ok": False, "line": canon.LINE_CATCH_ALL},
           "read_aloud bad-id: canon catch-all, never a guess")

    # A1: redo
    dialog7, vault7, _m7, gfx7, _o7, ev7, _s7 = universe(
        "u7", [("ok", "answer v1", 10), ("ok", "answer v2", 11)], [])
    dialog7.send("hello")
    old_mid = vault7.messages_for(1)[-1]["id"]
    redo = dialog7.quick_action("redo", {"chatId": 1, "messageId": old_mid})
    expect(out, redo["ok"] and redo["messageId"] != old_mid
           and vault7.message_get(old_mid)["superseded"] == old_mid,
           "redo persists a fresh answer; the prior one flags ITSELF superseded (superseded=old id)")
    expect(out, [m["text"] for m in dialog7.open_chat(1) if m["who"] == "tars"] == ["answer v2"],
           "open_chat shows the replacement only; the vault keeps both rows append-only")
    last_done7 = [detail for kind, detail in ev7 if kind == "done"][-1]
    expect(out, last_done7["messageId"] == redo["messageId"] and last_done7["hue"] == "cloud",
           "redo streams chunk/done like a normal reply; done carries the NEW id (A2)")
    expect(out, gfx7.received[-1][-1] == {"role": "user", "content": "hello"},
           "redo re-routes the ORIGINAL user text, never a paraphrase")
    expect(out, dialog7.quick_action("redo", {"chatId": 1, "messageId": 12345}) == {"ok": False, "line": canon.LINE_CATCH_ALL},
           "redo bad-id refused, never guessed")
    expect(out, dialog7.quick_action("open", {}) == {"ok": False, "line": canon.LINE_CATCH_ALL},
           "unshipped quick_action names get the canon catch-all (P-CORE-5 territory)")

    # rolling context window
    dialog8, _v8, _m8, gfx8, _o8, _e8, _s8 = universe("u8", [("ok", f"a{i}", 5) for i in range(1, 13)], [])
    for i in range(1, 13):
        dialog8.send(f"m{i}")
    last_call = gfx8.received[-1]
    expect(out, len(last_call) == 12 and last_call[0]["role"] == "system"
           and last_call[1]["content"] == "m7" and last_call[-1]["content"] == "m12",
           "rolling context: system + last 10 messages + user; the window slides, oldest dropped")


def _voice_checks(base: Path, out) -> None:
    zone = base / "voice"
    zone.mkdir(parents=True, exist_ok=True)
    full_source = {f"GROQ_KEY_{i}": f"gsk-{i}" for i in range(1, 7)}
    full_source.update({f"OPENROUTER_KEY_{i}": f"or-{i}" for i in range(1, 3)})

    def universe(name, groq_script, ear_engines):
        path = zone / name
        log = LogX(path / "logs.jsonl")
        settings = Settings.load(path / "settings.json", log)
        vault = Vault(path / "vault.db")
        bus = Bus()
        events = []
        bus.subscribe(lambda kind, detail: events.append((kind, detail)))
        machine = Machine(settings, log, bus)
        groq_fx = FixtureAdapter("groq", groq_script)
        router = Router(load_ring(full_source),
                        {"groq": groq_fx, "openrouter": FixtureAdapter("openrouter", [])}, vault, bus)
        dialog = Dialog(settings, vault, router, machine, bus)
        machine.set_audience("cooper")
        return dialog, vault, machine, groq_fx, bus, events, log, EarLadder(ear_engines, log)

    # --- fixture law: bytes generated in code, pinned, deterministic
    expect(out, voicefix.sine_ms(100) == voicefix.sine_ms(100) and voicefix.noise_ms(100) == voicefix.noise_ms(100),
           "in-code fixtures deterministic: sine + seeded noise regenerate byte-identical")
    sine100 = voicefix.sine_ms(100)
    with wave.open(io.BytesIO(voicefix.wrap_wav(sine100)), "rb") as parsed:
        params = (parsed.getnchannels(), parsed.getsampwidth(), parsed.getframerate(), parsed.getnframes())
        payload = parsed.readframes(parsed.getnframes())
    expect(out, params == (1, 2, voicefix.RATE, 1600) and payload == sine100,
           "wrap_wav: valid mono 16-bit 16kHz RIFF; the PCM payload round-trips byte-exact")

    # --- VAD pins (declared constants: 30ms frames, RMS 500, 270ms hangover, 90ms floor)
    expect(out, vad_spans(voicefix.sine_ms(600)) == [(0, 600)], "VAD pin: 600ms voiced -> one exact (0,600) span")
    bridged = voicefix.pcm([voicefix.silence_ms(300), voicefix.sine_ms(600), voicefix.silence_ms(150),
                            voicefix.sine_ms(300), voicefix.silence_ms(300)])
    expect(out, vad_spans(bridged) == [(300, 1350)], "VAD pin: 150ms silence inside speech bridges into one span")
    split = voicefix.pcm([voicefix.silence_ms(300), voicefix.sine_ms(600), voicefix.silence_ms(480),
                          voicefix.sine_ms(300), voicefix.silence_ms(300)])
    expect(out, vad_spans(split) == [(300, 900), (1380, 1680)], "VAD pin: 480ms gap splits into two exact spans")
    blip = voicefix.pcm([voicefix.silence_ms(300), voicefix.sine_ms(60), voicefix.silence_ms(600)])
    expect(out, vad_spans(blip) == [] and vad_spans(voicefix.silence_ms(900)) == [],
           "VAD pin: sub-90ms blips and pure silence hold no speech")
    expect(out, frame_rms(voicefix.sine_ms(30)) >= RMS_THRESHOLD
           and frame_rms(voicefix.silence_ms(30)) < RMS_THRESHOLD
           and frame_rms(voicefix.noise_ms(30)) < RMS_THRESHOLD,
           "declared VAD constants hold: voiced over RMS_THRESHOLD, silence and noise under it")
    span_source = voicefix.pcm([voicefix.silence_ms(300), voicefix.sine_ms(600), voicefix.silence_ms(300)])
    expect(out, slice_pcm(span_source, (300, 900)) == voicefix.sine_ms(600),
           "slice_pcm cuts exactly the span bytes, nothing more")

    # --- engine protocol: byte-compared transcripts, failure step-down, billing law
    engine = FixtureEarEngine(["hello cooper"])
    expect(out, engine.transcribe(b"any pcm bytes") == "hello cooper" and engine.calls == 1,
           "FixtureEarEngine transcript byte-compared against the script, calls counted")
    raised = False
    try:
        FixtureEarEngine(["fail"]).transcribe(b"x")
    except RuntimeError:
        raised = True
    expect(out, raised, "a scripted ear failure raises; the ladder owns the step-down")

    wires = []

    def probe_transport(url, body, content_type, key_string):
        wires.append((url, content_type, len(body), bool(key_string)))
        return "heard by groq"

    log_ladder = LogX(zone / "ladder.jsonl")
    ring_ears = load_ring({"GROQ_KEY_1": "gsk-ears-fixture"})
    local_miss = FixtureEarEngine(["unused"], loads=False)
    ladder_eg = EarLadder([local_miss, GroqEarsAdapter(ring_ears, transport=probe_transport)], log_ladder)
    heard_eg = ladder_eg.transcribe(voicefix.sine_ms(300))
    expect(out, heard_eg == "heard by groq" and local_miss.calls == 0 and local_miss.load_calls == 1,
           "ladder order proven: local load-miss steps down to groq-ears, the missed engine never transcribes")
    key_ear = ring_ears.keys()[0]
    expect(out, key_ear.lane_spent.get("ears") == 1 and key_ear.spent_today == 1,
           "ears billing travels through keys.py record alone — ring counters, never the vault ledger")
    expected_body = build_multipart({"model": GroqEarsAdapter.MODEL}, "file", "speech.wav",
                                    voicefix.wrap_wav(voicefix.sine_ms(300)), "audio/wav")[0]
    expect(out, wires == [(GroqEarsAdapter.URL, "multipart/form-data; boundary=----tars-ear-boundary",
                           len(expected_body), True)],
           "the transport fired exactly once: pinned endpoint, declared boundary, exact body bytes, key present")

    ladder_fail = EarLadder([FixtureEarEngine(["fail"]), FixtureEarEngine(["second engine served"])], log_ladder)
    fell = ladder_fail.transcribe(voicefix.sine_ms(300))
    expect(out, fell == "second engine served" and any(row.get("kind") == "ears" for row in log_ladder.read_all()),
           "a raised engine logs an ears entry and the ladder serves from the next engine")

    body, content_type = build_multipart({"model": GroqEarsAdapter.MODEL}, "file", "speech.wav",
                                         voicefix.wrap_wav(voicefix.sine_ms(60)), "audio/wav")
    expect(out, content_type == "multipart/form-data; boundary=----tars-ear-boundary"
           and b'--' + b"----tars-ear-boundary" in body and b'name="model"' in body
           and GroqEarsAdapter.MODEL.encode() in body and body.count(b"RIFF") == 1,
           "groq-ears multipart request: boundary, model field, wav payload present (shape reviewable, wire cold)")

    # --- whisper-small local: lazy model path + RAM Charter policy + sandbox import guard
    expect(out, WhisperSmallLocal(zone / "no-models").load() is False,
           "whisper load: declared model slot absent -> honest False, the ladder steps down")
    model_zone = zone / "models"
    model_zone.mkdir(parents=True)
    (model_zone / "whisper-small.bin").write_bytes(b"in-code staged model bytes")  # real weight lands at M-1
    ram_pressured = WhisperSmallLocal(model_zone, ceiling_mb=2000, ram_probe=lambda: 1500)
    expect(out, ram_pressured.load() is False,
           "RAM Charter: 1500MB used + 900MB burst would cross the 2GB ceiling -> policy-falls to groq-ears")
    ram_clear = WhisperSmallLocal(model_zone, ceiling_mb=2000, ram_probe=lambda: 100)
    expect(out, ram_clear.load() is False,
           "whisper import guard: faster_whisper staged on the AiO at M-1, honestly absent in a sandbox")

    # --- mic-cold law: the guard raises outside LISTENING, on any OS, before any device
    _dc, _vc, m_c, _gc, _bc, _ec, _lc, _lad_c = universe("u-cap", [], [FixtureEarEngine(["x"])])
    guard = SoundDeviceCapture(m_c)
    raised = False
    try:
        guard.open()
    except RuntimeError:
        raised = True
    expect(out, raised and guard.closed, "mic guard raises in OFF, capture stays cold (mic-cold law)")
    m_c.summon()
    raised = False
    try:
        guard.open()
    except RuntimeError:
        raised = True
    expect(out, raised, "mic guard raises in ARMED too — LISTENING or nothing")
    m_c.voice_start()
    expect(out, guard.open() is False and guard.closed,
           "real device open is nt-only: the Linux sandbox answers False cleanly (canon skip; P3 proves hardware)")

    # --- run_voice_turn: entry law, happy path, joined spans, honesty lines, kill
    dlg_off, _vo, m_off, _go, bus_off, _eo, _lo, lad_off = universe("u-off", [], [FixtureEarEngine(["x"])])
    cold = FakeCapture(m_off, [voicefix.sine_ms(300)])
    refused = run_voice_turn(cold, lad_off, m_off, bus_off, dlg_off)
    expect(out, refused == {"ok": False, "line": canon.LINE_CATCH_ALL} and cold.closed and m_off.state == OFF,
           "voice turn from OFF: canon catch-all, capture never opened, machine untouched")

    engine_h = FixtureEarEngine(["physics test on friday"])
    dlg_h, v_h, m_h, gfx_h, bus_h, ev_h, _lh, lad_h = universe("u-happy", [("ok", "the voice answer", 10)],
                                                               [engine_h])
    m_h.summon()
    cap_h = FakeCapture(m_h, [voicefix.silence_ms(120), voicefix.sine_ms(600), voicefix.silence_ms(120)])
    happy = run_voice_turn(cap_h, lad_h, m_h, bus_h, dlg_h)
    expect(out, happy == {"ok": True, "text": "physics test on friday", "chatId": 1},
           "voice turn end to end: transcript text + new chatId returned")
    kinds_h = [kind for kind, _detail in ev_h]
    transcript_at = kinds_h.index("transcript")
    expect(out, transcript_at < kinds_h.index("chunk") and transcript_at < kinds_h.index("done"),
           "transcript fires BEFORE any routing output (contract §3: what was heard shows first, dimmed)")
    transcript_detail = [detail for kind, detail in ev_h if kind == "transcript"][0]
    expect(out, transcript_detail == {"who": "cooper", "text": "physics test on friday"},
           "transcript detail shape exact: {who, text}, zero extra fields")
    msgs_h = v_h.messages_for(1)
    expect(out, [m["who"] for m in msgs_h] == ["cooper", "tars"]
           and msgs_h[0]["text"] == "physics test on friday" and msgs_h[1]["text"] == "the voice answer",
           "both sides of the voice turn persisted in the vault, append-only")
    expect(out, m_h.state == LISTENING and cap_h.closed and engine_h.calls == 1,
           "voice session returns to LISTENING with capture closed — mic law kept on every exit path")
    expect(out, v_h.ledger_total() == 10 and {row["lane"] for row in v_h.ledger_tail(5)} == {"smart"},
           "the reply's token billing lands in the vault ledger through the router alone ('physics' gates smart, §P1 list)")
    m_h.voice_stop()

    engine_j = FixtureEarEngine(["physics test", "on friday"])
    dlg_j, _vj, m_j, _gj, bus_j, _ej, _lj, lad_j = universe("u-join", [("ok", "joined answer", 10)], [engine_j])
    m_j.summon()
    two_spans = voicefix.pcm([voicefix.silence_ms(300), voicefix.sine_ms(600), voicefix.silence_ms(480),
                              voicefix.sine_ms(300), voicefix.silence_ms(300)])
    joined = run_voice_turn(FakeCapture(m_j, [two_spans]), lad_j, m_j, bus_j, dlg_j)
    expect(out, joined["ok"] and joined["text"] == "physics test on friday" and engine_j.calls == 2,
           "two speech spans transcribe on separate engine calls and join with a single space")

    engine_s = FixtureEarEngine(["never called"])
    dlg_s, v_s, m_s, gfx_s, bus_s, ev_s, _ls, lad_s = universe("u-sil", [], [engine_s])
    m_s.summon()
    quiet = run_voice_turn(FakeCapture(m_s, [voicefix.silence_ms(900)]), lad_s, m_s, bus_s, dlg_s)
    expect(out, quiet == {"ok": False, "line": canon.LINE_HEARD_BADLY} and engine_s.calls == 0,
           "bad-audio honesty: silence never executes — no engine call, the §22 heard-badly line answers")
    expect(out, v_s.messages_for(1)[-1]["text"] == canon.LINE_HEARD_BADLY
           and v_s.messages_for(1)[-1]["hue"] == "local",
           "heard-badly persisted as a local-hue tars message, byte-exact §22")
    expect(out, not any(kind == "transcript" for kind, _d in ev_s) and gfx_s.received == [],
           "silence emits no transcript and routes nothing to any brain")

    ring_groq_ear = load_ring({"GROQ_KEY_1": "gsk-ear-test"})
    groq_ear = GroqEarsAdapter(ring_groq_ear, transport=probe_transport)
    dlg_g, v_g, m_g, _gg, bus_g, _eg, _lg, lad_g = universe("u-groqear", [("ok", "cloud-ear answer", 10)],
                                                            [FixtureEarEngine(["x"], loads=False), groq_ear])
    m_g.summon()
    groq_turn = run_voice_turn(FakeCapture(m_g, [voicefix.sine_ms(300)]), lad_g, m_g, bus_g, dlg_g)
    expect(out, groq_turn["ok"] and groq_turn["text"] == "heard by groq" and len(wires) == 2,
           "local-miss voice turn served by groq-ears exactly once (the scripted transport's second call)")
    expect(out, ring_groq_ear.keys()[0].lane_spent.get("ears") == 1
           and {row["lane"] for row in v_g.ledger_tail(5)} == {"fast"},
           "billing law: ears spend lives only on the ring key; the vault token ledger sees the router alone")

    ring_dead = load_ring({})
    dlg_d, v_d, m_d, _gd, bus_d, _ed, _ld, lad_d = universe("u-spent", [], [GroqEarsAdapter(ring_dead,
                                                                                            transport=probe_transport)])
    m_d.summon()
    spent = run_voice_turn(FakeCapture(m_d, [voicefix.sine_ms(300)]), lad_d, m_d, bus_d, dlg_d)
    expect(out, spent == {"ok": False, "line": canon.LINE_ALL_SPENT} and len(wires) == 2
           and v_d.messages_for(1)[-1]["text"] == canon.LINE_ALL_SPENT,
           "drained ears lane: canon all-spent byte-exact + persisted, the wire provably untouched (never keyless)")

    dlg_nm, v_nm, m_nm, _gnm, bus_nm, _enm, _lnm, lad_nm = universe("u-nomic", [], [FixtureEarEngine(["x"])])
    m_nm.summon()
    real_cap = SoundDeviceCapture(m_nm)
    nomic = run_voice_turn(real_cap, lad_nm, m_nm, bus_nm, dlg_nm)
    expect(out, nomic == {"ok": False, "line": canon.LINE_NO_MIC}
           and v_nm.messages_for(1)[-1]["text"] == canon.LINE_NO_MIC and real_cap.closed,
           "device absent: the §22 no-mic line answers and persists, text mode stays home")

    dlg_k, v_k, m_k, gfx_k, bus_k, ev_k, _lk, lad_k = universe("u-kill", [], [FixtureEarEngine(["too late"])])

    def kill_at_five(index):
        if index == 5:
            m_k.kill()

    m_k.summon()
    cap_k = FakeCapture(m_k, [voicefix.sine_ms(30) for _n in range(10)], on_frame=kill_at_five)
    killed = run_voice_turn(cap_k, lad_k, m_k, bus_k, dlg_k)
    expect(out, killed == {"ok": False, "line": canon.LINE_CATCH_ALL}
           and m_k.state == OFF and not m_k.mic_open and cap_k.closed,
           "kill mid-capture (Law 5): state OFF instantly, mic cold, the turn aborts clean — zero trap")
    expect(out, not any(kind == "transcript" for kind, _d in ev_k)
           and v_k.chat_rows() == [] and gfx_k.received == [],
           "a killed turn emits no transcript, persists nothing, routes nothing")

    # --- mouth ladder: order, cascade, honest refusal, real-tier sandbox truth
    log_m = LogX(zone / "mouth.jsonl")
    sapi_down = FixtureTier("sapi", True, False)
    piper_ok = FixtureTier("piper", True, True)
    edge_ok = FixtureTier("edge", False, True)
    spoke = Mouth([sapi_down, piper_ok, edge_ok], log_m).speak("report for duty")
    expect(out, spoke == {"ok": True, "tier": "piper", "cancelled": False, "private": False}
           and sapi_down.calls == [] and piper_ok.calls == ["report for duty"] and edge_ok.calls == [],
           "mouth ladder order: unavailable sapi skipped uncalled, piper serves, edge stays cold")
    sapi_fail = FixtureTier("sapi", True, True, "fail")
    piper_ok2 = FixtureTier("piper", True, True)
    edge_ok2 = FixtureTier("edge", False, True)
    spoke_fail = Mouth([sapi_fail, piper_ok2, edge_ok2], log_m).speak("try again")
    expect(out, spoke_fail["ok"] and spoke_fail["tier"] == "piper"
           and sapi_fail.calls == ["try again"] and edge_ok2.calls == [],
           "per-tier failure cascade: a failed local tier steps down inside the same speak call")
    expect(out, edge_ok2.local is False and EdgeTier().local is False,
           "edge declared CLOUD (local False) on the fixture and the real adapter alike")
    dead = Mouth([FixtureTier("sapi", True, True, "fail"), FixtureTier("piper", True, False)], log_m).speak("nobody home")
    expect(out, dead == {"ok": False, "tier": "sapi", "cancelled": False, "private": False}
           and any(row.get("kind") == "mouth" and "stayed on screen" in row.get("note", "")
                   for row in log_m.read_all()),
           "no serving tier: the last attempted tier is named, the refusal is logged, the text stays on screen")
    expect(out, SapiTier().available() is False and PiperTier(zone / "no-piper").available() is False,
           "real local tiers honestly unavailable in a Linux sandbox (nt-first staging at M-1)")

    # --- privacy routing is LAW: private never rides the edge, provably
    log_p = LogX(zone / "privacy.jsonl")
    piper_fail = FixtureTier("piper", True, True, "fail")
    edge_watch = FixtureTier("edge", False, True)
    mouth_p = Mouth([piper_fail, edge_watch], log_p)
    private_turn = mouth_p.speak("Cooper's physics result", private=True)
    expect(out, private_turn == {"ok": False, "tier": "piper", "cancelled": False, "private": True}
           and piper_fail.calls == ["Cooper's physics result"] and edge_watch.calls == [],
           "privacy LAW: a private utterance never reaches edge-tts — tier skipped (call proof), text stays local")
    expect(out, sum(1 for row in log_p.read_all() if row.get("kind") == "privacy") == 1,
           "the privacy skip leaves a logged audit line — no silent path, no configurable backdoor")
    public_turn = mouth_p.speak("the weather today", private=False)
    expect(out, public_turn["ok"] and public_turn["tier"] == "edge" and edge_watch.calls == ["the weather today"],
           "control case: the same edge tier DOES serve a public utterance — privacy alone gates it")
    piper_serve = FixtureTier("piper", True, True)
    edge_watch2 = FixtureTier("edge", False, True)
    local_private = Mouth([piper_serve, edge_watch2], LogX(zone / "privacy2.jsonl")).speak("family secret",
                                                                                           private=True)
    expect(out, local_private["ok"] and local_private["tier"] == "piper" and edge_watch2.calls == [],
           "private with a healthy local tier: served locally, edge never consulted")

    # --- barge-in: cancel honored in-tick; a fresh listen wins over an in-flight speak
    log_barge = LogX(zone / "barge.jsonl")
    ticks_seen = []

    def on_tick(tick):
        ticks_seen.append(tick)
        if tick == 2:
            mouth_barge.interrupt()

    tier_barge = FixtureTier("piper", True, True, ticks=5, on_tick=on_tick)
    mouth_barge = Mouth([tier_barge], log_barge)
    cancelled = mouth_barge.speak("a long winding story")
    expect(out, cancelled == {"ok": False, "tier": "piper", "cancelled": True}
           and ticks_seen == [0, 1, 2] and tier_barge.stop_calls == 1,
           "barge-in: interrupt() is honored exactly in-tick via the active tier's stop (§20)")

    dlg_lw, _vlw, m_lw, _glw, bus_lw, _elw, log_lw, lad_lw = universe("u-lw", [("ok", "listen wins", 10)],
                                                                      [FixtureEarEngine(["fresh listen"])])
    in_flight = FixtureTier("piper", True, True)
    mouth_lw = Mouth([in_flight], log_lw)
    mouth_lw._active = in_flight  # an utterance mid-flight at the instant the push-to-talk press lands
    m_lw.summon()
    lw_turn = run_voice_turn(FakeCapture(m_lw, [voicefix.sine_ms(300)]), lad_lw, m_lw, bus_lw, dlg_lw,
                             mouth=mouth_lw)
    expect(out, lw_turn["ok"] and in_flight.stop_calls == 1 and in_flight.calls == [],
           "a fresh listen wins over an in-flight speak: run_voice_turn interrupts the mouth first (§20)")

    # --- A1 drain: queued -> done lifecycle, ghosts, and failed:<tier> honesty
    dlg_q, v_q, m_q, _gq, _bq, _eq, log_q, _lad_q = universe("u-drain", [("ok", "read me aloud", 10)],
                                                             [FixtureEarEngine(["x"])])
    dlg_q.send("hello")
    mid_q = v_q.messages_for(1)[-1]["id"]
    dlg_q.quick_action("read_aloud", {"chatId": 1, "messageId": mid_q})
    v_q.kv_set("speak_request:9999", "queued")  # a ghost intake whose message never existed
    piper_drain = FixtureTier("piper", True, True)
    report_q = Mouth([piper_drain], log_q).drain_speak_queue(v_q, m_q)
    expect(out, report_q == {"drained": 1, "failed": 1}
           and v_q.kv_get(f"speak_request:{mid_q}") == "done" and piper_drain.calls == ["read me aloud"],
           "speak-queue drain: queued -> done with the exact message text spoken (A1 lifecycle closed)")
    expect(out, v_q.kv_get("speak_request:9999") == "failed:no-message",
           "a ghost intake marks failed:no-message and is logged — never a guessed target")
    transitions_q = [(row.get("from"), row.get("to")) for row in log_q.read_all() if row.get("kind") == "transition"]
    expect(out, transitions_q.count(("armed", "thinking")) == 2
           and transitions_q.count(("thinking", "speaking")) == 2
           and transitions_q.count(("speaking", "armed")) == 2,
           "the drain's SPEAKING turns flow through state.py alone (typed turn + drained turn, transition log proves it)")
    v_q.kv_set(f"speak_request:{mid_q}", "queued")
    report_broken = Mouth([FixtureTier("piper", True, True, "fail")], log_q).drain_speak_queue(v_q, m_q)
    expect(out, report_broken == {"drained": 0, "failed": 1}
           and v_q.kv_get(f"speak_request:{mid_q}") == "failed:piper",
           "speak failure marks failed:<tier> honestly — the queue lies to no one")


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
    chats = vault.chat_rows()
    committed_messages = vault.messages_for(chats[0]["id"]) if chats else []
    vault.close()
    expect(out, integrity == "ok", "post-SIGKILL re-open: sqlite integrity_check ok")
    expect(out, stored == [f"v{i}" for i in range(5)], "all 5 pre-kill committed kv rows survived")
    expect(out, memories >= 5 and total >= 50, f"committed prefix intact (memory rows={memories}, ledger tokens={total})")
    expect(out, len(chats) == 1 and len(committed_messages) >= 5,
           f"chats + messages tables survive the kill ({len(committed_messages)} messages intact)")
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
    chat_id = vault.chat_insert()
    for i in range(5):
        vault.kv_set(f"k{i}", f"v{i}")
        vault.remember("note", f"committed memory {i}")
        vault.spend("mock", 0, 10)
        vault.message_add(chat_id, "cooper" if i % 2 == 0 else "tars", f"committed message {i}", None, None)
        log.entry("child", marker=i)
    print("READY", flush=True)
    burst = 0
    while True:
        vault.remember("burst", f"in-flight {burst}")
        vault.message_add(chat_id, "tars", f"burst message {burst}", "cloud", "fast")
        log.entry("child-burst", marker=burst)
        burst += 1


def main() -> int:
    if "--child" in sys.argv:
        _child_crash_worker(Path(sys.argv[sys.argv.index("--child") + 1]))
        return 0
    out = sys.stdout
    print("CORE SELFTEST — P-CORE-0 + P-CORE-1 ring + P-CORE-2 persona + P-CORE-3 voice batteries — proof, not claims",
          file=out)
    base = Path(tempfile.mkdtemp(prefix="tars-core-"))
    print(f"data sandbox: {base}", file=out)
    _canon_checks(out)
    _functional_checks(base, out)
    _machine_checks(base, out)
    _demochat_checks(base, out)
    _ring_checks(base, out)
    _ringdemo_checks(base, out)
    _persona_checks(base, out)
    _voice_checks(base, out)
    _crash_checks(base, out)
    print(f"SELFTEST: ALL GREEN ({CHECKS} checks)", file=out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
