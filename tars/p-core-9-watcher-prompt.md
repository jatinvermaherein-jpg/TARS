# P-CORE-9 — WATCHER (operator prompt · Strict-Prompt Doctrine)
**Lane:** AGENT CORE only · **Jurisdiction:** `tars/core/` + ONE sanctioned append to `tars/agent-log.md` + ONE sanctioned doc bump: `tars/command-grammar.md` → **v1.4** (APPEND-ONLY; v1.0–v1.3 bytes untouched — zero-removed-lines diff is the standing proof). `tars/app/` frozen. Nothing else.
**Base:** branch `main` at `3745e8e` (P-CORE-8 tree, **495 checks green**, audit banked Aug 20). All 495 stay green and byte-stable except the ONE expected re-aim (§7).
**Date:** 2026-08-20 · suite chain 62→96→138→193→243→320→385→445→495.

---

## 0. Read order (never skip)
1. `tars/tars-definition.md` v1.2 — **§29 (meter = visibility, not enforcement)** · **§32 (state machine; Law 3: after power cuts TARS boots OFF; first summon after = the survival report)** · the canon flavor at line 62: *"Power event at 8:41 PM. Memory intact. Nothing lost."* · Law 7 (storage uncapped, meter only) · §11 canon lines.
2. `tars/roadmap.md` P-CORE-9 row — acceptance: **gauge math selftest · drill state-restore test**.
3. `tars/bridge-contract.md` v1.4 — quick_action `'status'` is rostered (line 48) and currently answered by the canon catch-all. This phase earns it. Channels CLOSED; bus stays exactly 9.
4. Standing tree: `gauge.py` (P-CORE-1 math — EXTEND its read surface, never fork it) · `keys.py` (LANE_CAPS, spent/warn/reset law) · `dailyops.py` (meter reads: storage/RAM — REUSE the one ops seam) · `vault.py` (WAL+FULL posture) · `clockd.py` (tick) · `state.py` (summon/dirty-shutdown truth) · `canon.py` (generative + literal-pin law).

## 1. What P-CORE-9 builds
**The desk learns to read its own pulse — and to confess a power cut without being asked.**

- `tars/core/watcher.py` — NEW. The health reader:
  - **Gauge report:** `gauge_report()` reads the LIVE 8-key ring state (per-key spent / lane caps / warn at 20% remaining / midnight reset) and renders an honest numbered summary. Number-words law for spoken acks; reports may carry digits within a plain list line (they're reports, not acks — declare the final voice in code and pin literals either way). All math from `keys.py`/`gauge.py` as they stand — zero duplicated counter logic.
  - **Storage meter (§29):** `storage_report()` — vault.db size, `tars-brain/` size, free-disk (via the existing dailyops seam). Meter only, NEVER enforcement: the render must include the visibility-not-enforcement doctrine in a canon comment; no code path may refuse/warn-block on size. (A gentle *advisory* line past a declared soft-mark is lawful — visibility — but it never blocks, never deletes.)
  - **RAM pressure:** `ram_report()` — reading (nt ops seam / psutil-guarded / fixture) or the canon unavailable line. Never an invented number (standing §16 law).
  - **Startup-creep watch:** baseline snapshot of auto-start entries (nt: READ-ONLY registry Run-key enumeration via `winreg` ON NT ONLY, canon comment per call; off-nt: fixture snapshot). `creep_report()` diffs baseline vs now → honest list of additions ("SpotifyWebHelper added itself to startup.") or the clean line. **LAW: TARS itself must never appear in any startup set** — a battery check asserts the watcher flags ANY injected `tars`-named creep entry as a violation line (Law 3, self-policing).
  - **Status assembly:** `status_report()` = the one-shot digest (keys gauge + storage + RAM + creep + uptime) that powers both the `status` grammar row and the rostered `quick_action('status')`.
- **The power-cut drill (§32 + line 62 flavor):**
  - Dirty-shutdown truth: vault carries a session heartbeat/clean-exit marker; a run that ends without stand-down leaves the marker dirty.
  - **Boot stays OFF** after any outage — Law 3, non-negotiable; nothing in this phase may auto-summon.
  - On the FIRST summon after a dirty end, TARS speaks the survival report ONCE, before answering anything else: intact case → `power_event_line("8:41 PM")` → `"Power event at 8:41 PM. Memory intact. Nothing lost."` (generative + literal-pinned; time from the heartbeat). Damage case → an honest variant naming what was lost (declare the shape, pin one literal; the append-only laws make damage rare, so the line must never be sadder than the truth nor happier).
  - Drill battery: `kill -9` mid-write → reopen → integrity probe → summon → line fired exactly once → cleared (a SECOND summon must NOT repeat it) → the restoration-state test asserts the machine resumes exactly where state.py left it.
- `command.py` — v1.4 rows: "status report" · "how are the keys" · "storage status" · "is ram ok" (reading-or-honest-line) · "startup check" / "what's creeping in" → creep_report · closed Hinglish aliases declared (suggest `status bata` — adjust but CLOSED). **Every watcher row is pure LOCAL read → ZERO ring spend, counter-pinned.**
- `dialog.py` — `quick_action('status')` SERVED by `status_report()` (the ONE expected re-aim — see §7).
- `canon.py` — extend, generative + literal-pinned:
  - `power_event_line(when)` (intact) + damage variant (§1) · `LINE_STARTUP_CLEAN = "Startup is clean. Nothing crept in."` · `LINE_CREEP_VIOLATION` shape for the self-policing line (name the shape, pin one literal — suggested bytes: `f"{name} added itself to startup. Your call whether it stays."`) · gauge/storage/RAM report family (pin ≥3 literal renders against fixture states, including a 20%-warn crossing and a midnight-reset case).

## 2. Ring discipline + honesty (battery PROVES, never claims)
- ALL watcher rows: zero adapter calls, counter-pinned (status/gauge/storage/creep reports are LOCAL reads; the machine's pulse never needs the cloud).
- Reading-or-honest-line law: off-nt/seam-absent meters answer the canon unavailable line, never a fabricated digit (pattern from P-CORE-6 pinned, re-pinned here).
- §29 comment law: storage code carries the visibility-not-enforcement canon comment; no enforcement branch exists anywhere — grep-level battery pin (a "creep" of enforcement logic is itself a violation).

## 3. Grammar v1.4 (append-only; 3 example utterances per row)
Rows: status · keys-gauge · storage · RAM · startup-creep. Row-for-row exercised; zero-ring counter-pinned.

## 4. Crash, determinism, guards
- Crash child gains the drill workload (kill → reopen → survival-line-once + state restore).
- urlopen/subprocess patched-to-RAISE extended over watcher.py.
- All 495 prior checks byte-stable except §7. Determinism ×2 minimum. Expect ≈540–560.

## 5. Agent-log (one append-only entry)
What shipped · gauge midnights/warn math · drill marker design · machine-taught fixes in the open · acceptance CORRECTION for P-CORE-8: "PASS, banked by Architect audit Aug-20 atop 3745e8e — 495/495 re-run twice, FRAME-CANARY pixel-exact re-verified, classifier==frames in every mode, bounds triad + truthful-idle pinned, 'look' re-aim exactly the sanctioned one."

## 6. Deliverable + REPORT block (§3.5 shape — mandatory)
Whole files only · zero dead code · zero unused imports (documented re-export/presence-probe patterns recognized) · zero >U+2100 glyphs · zero new deps · zero network.
Commit: `[CORE] P-CORE-9 — Watcher: live key gauge + storage/RAM meters, startup-creep watch, §32 power-cut drill with one-time survival report, 'status' chip served, grammar v1.4, <N>-check selftest`.
REPORT: FILES (line counts) · 7-LAWS RECITAL · SELFTEST OUTPUT (fresh-clone tail, twice) · CONTRACT CHECK (channels closed, bus at 9, 'status' chip served) · KNOWN LIMITS (winreg reads nt-real/AiO-era; fixtures here) · RE-AIMS · PUSHED (short hash, fresh-clone-verified green).

## 7. The ONE sanctioned re-aim
`'status'` LEAVES the unshipped quick_action catch-all set; the remaining roster names re-pin the catch-all byte-exact. Disclose in-code + REPORT. Any further diffs to prior checks = FAIL.

**Never List + 7 Laws bind. §29's word is the phase: the meter shows; nothing cages; and when the power dies, TARS tells Cooper what survived before he thinks to ask. The machine's truth over green lights. Make the pulse honest.**
