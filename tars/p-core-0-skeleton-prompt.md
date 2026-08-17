# P-CORE-0 — SKELETON + STATE MACHINE (CORE lane · main agent · build prompt)
**Paste this entire block to AGENT CORE after feeding `tars-definition.md` v1.1 and getting its 7-Laws recital. First build prompt of the Core lane.**

---

You are AGENT CORE building the soul of TARS, a resident desktop AI crew member (bible `tars/tars-definition.md` v1.1 — it wins every conflict). READ first, in order: bible · `tars/bridge-contract.md` v1.0 · `tars/roadmap.md` §3 (Strict-Prompt Doctrine — verbatim compliance) and §6 (your phase map). Then state the 7 Laws in one line. If you can't, STOP.

**JURISDICTION:** you write ONLY inside `tars/core/`. UI is APP's territory — you speak to it only through `bridge-contract.md` shapes. No pywebview yet (merge is P3) — this phase is headless and must prove itself headless.

**ENVIRONMENT:** sandbox is Linux; target is Windows 11 x86 AiO, Python 3.12. Write Windows-correct code (`pathlib`, no hardcoded `/`) that also passes here. Any Windows-only call goes behind a `os.name == "nt"` adapter with a canon one-line comment. Dependencies this phase: **standard library only** (sqlite3, json, threading, signal, dataclasses, enum, argparse, datetime). No pip yet.

**SHIP (whole files; zero dead code per §3 — every function reached by the selftest below):**
1. `tars/core/state.py` — the bible §32 state machine: `OFF →(summon)→ ARMED → LISTENING ⇄ THINKING ⇄ SPEAKING →(stand-down/10-min-idle)→ OFF` · ERROR yields the prior state, never traps · kill-switch from ANY state is instant and unconditional · expose the exact `StateNotice` shape from contract §3 (state, dials, audience, lane, hue) as the single emit path.
2. `tars/core/settings.py` — `settings.json` load/save (atomic tmp-then-rename), the five dials §10 with HONESTY hard-refused at every path (`set_dial("honesty", …)` returns exactly `{"ok": false, "line": "Honesty is fixed at ninety."}`), corrupt-file recovery to factory defaults with a logged line.
3. `tars/core/vault.py` — `vault.db` SQLite, append-only writes, WAL mode, crash-safe; tables: `kv` (name/date), `memory` (ts, kind, text), `ledger` (ts, lane, keyindex, tokens) per bible §30 ledger spirit.
4. `tars/core/logx.py` — `logs.jsonl` append-only, fsync'd; every state transition + dial change + error logged.
5. `tars/core/canon.py` — every canon line from bible §11 byte-exact as constants (boot, exit, cloud-fail, all-spent, no-network, catch-all, never-list, confirm/cancel, post-handover). Single source; other modules import from here only.
6. `tars/core/bus.py` — an in-process event emitter exposing exactly the contract `__tarsEvent` types (state/chunk/done/action/transcript/gauge/error/close); the pywebview wire replaces the transport at merge without touching emitters.
7. `tars/core/__main__.py` — `--demochat` headless run: simulated summon → boot line emitted → typed "humor 60" → canon confirm → "status" → a THINKING→SPEAKING exchange with LOCAL hue → "shutdown" emits `action` (red-verb) then cancel → "Cancelled. Nothing changed." → stand down → OFF → all transitions visible on stdout with timestamps.
8. `tars/core/selftest.py` — runs the demo twice, **kills the process mid-write once (os._kill-style)** and proves zero vault/log corruption on re-open (line counts + sqlite integrity check), asserts honesty-refusal byte-exactness, asserts kill-from-LISTENING leaves state OFF and mic-flag cold.

**FORBIDDEN:** emoji · TODOs/placeholders · commented-out code · unused imports · features from later phases (no router, no audio, no operator verbs — P-CORE-0 ends where it ends) · writing outside `tars/core/`.

**REPORT:** roadmap §3.5 block, verbatim selftest stdout included.

---

## §3.5 REPORT BLOCK (paste verbatim at the end)
```
LANE: CORE · PHASE: P-CORE-0 · DATE:
FILES: <path — lines> …
7-LAWS RECITAL: <one line>
SELFTEST OUTPUT: <verbatim stdout incl. crash-restart proof>
CONTRACT CHECK: StateNotice-shape=PASS/FAIL · canon-byte-exact=PASS/FAIL · crash-safe=PASS/FAIL · kill-switch=PASS/FAIL · zero-dead-code=PASS/FAIL
KNOWN LIMITS: <honest lines>
PUSHED: <commit hash, "[CORE] P-CORE-0 …">
```
