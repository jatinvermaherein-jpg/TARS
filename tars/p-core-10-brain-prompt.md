# P-CORE-10 — THE LIVING BRAIN (operator prompt · Strict-Prompt Doctrine)
**Lane:** AGENT CORE only · **Jurisdiction:** `tars/core/` + ONE sanctioned append to `tars/agent-log.md` + ONE sanctioned doc bump: `tars/command-grammar.md` → **v1.5** (APPEND-ONLY; v1.0–v1.4 bytes untouched). `tars/app/` frozen. Nothing else.
**Base:** branch `main` at `8240333` (P-CORE-9 tree, **540 checks green**, audit banked Aug 20). All 540 stay green and byte-stable except the §7-sanctioned re-aims.
**Date:** 2026-08-20 · suite chain …→320→385→445→495→540.

---

## 0. Read order (never skip)
1. `tars/tars-definition.md` v1.2 — **PART VI-B §25.5, the scripture**: the `tars-brain/` directory is a *brain, not a cache* — human-readable markdown/JSON, inspectable by Cooper anytime, **no size limit (§29), it grows for life** · people profiles / knowledge notes / daily journal / reflections & lessons / plans · **privacy law: 100% local, never spoken to unrecognized voices, never cloud-synced, wiped at Handover** (Handover itself is P-CORE-11 — do NOT build the wipe, zero dead code).
2. `tars/roadmap.md` P-CORE-10 row — acceptance: **consolidation selftest: journal folds → profiles update → tomorrow's recall**.
3. `tars/bridge-contract.md` v1.4 — **A3 (contract line 10, 46-47): `list_brain(path) -> BrainNode[]` {path, kind:'dir'|'file', sizeKb, modifiedDay} and `brain_text(path) -> string` are THIS phase's earned bridge surface**, read-only Living Brain explorer. Channels otherwise CLOSED; bus stays exactly 9.
4. Standing tree: `vault.py` (memory capture feeding the journals), `persona.py` (memory block assembly), `clockd.py` (sleep-cycle tick), `canon.py`, `selftest.py` (FixtureAdapter scripting, CANARY shapes, crash child).

## 1. What P-CORE-10 builds
**TARS stops renting context and starts owning a mind.**

- `tars/core/brain.py` — NEW. The Living Brain:
  - **The tree** (declared in code, human-readable, markdown): `tars-brain/` under `TARS_DATA` (nt truth comment: `C:\TARS\data\tars-brain\` on the AiO) — `people/` (one evolving profile per known person) · `journal/YYYY-MM-DD.md` (the day's raw record) · `lessons/` (rules written from mistakes) · `knowledge/` (distilled "remember this" captures) · `plans/` (things in motion) · `inner/` (the Inner-Voice journal, §1 privacy below). Every write is **atomic tmp-then-rename** (standing crash-safe law).
  - **Daily journal:** the day folds in at stand-down / sleep-cycle tick (reuse the standing cadence): what happened, what Cooper asked, what went wrong — fixture-grade composition, deterministic, honest (records only what truly passed through the machine this run; an empty day writes no journal).
  - **Self-curation + consolidation pass:** `consolidate()` folds today's journal into profiles/lessons/knowledge — **ring-bounded by decree: at most TWO smart-lane calls per pass** (fixture in sandbox); ring spent/unavailable → consolidation honestly DEFERRED and journaled as deferred (never faked, never retried in a storm). Roadmap acceptance is the battery: **journal folds → profiles update → tomorrow's recall** — teach something day 1, consolidate, summon day 2, the recalled/persona surface carries the distillation. Pin it end-to-end.
  - **Inner-Voice private journal:** `inner/` is TARS's own page. Sovereignty law: inner-voice bytes NEVER appear in any ring payload, NEVER spoken to a non-Cooper audience (guest/family ask → the canon refusal), NEVER leave the machine. Battery proves all three (canary-swept per the CLIP/SEND/FRAME pattern).
  - **A3 explorer (the earned bridge surface):** `list_brain(path)` → BrainNode[] with honest sizes (sizeKb) and modifiedDay; `brain_text(path)` → leaf preview string. **Path-confinement LAW: every path resolves INSIDE the tars-brain root — `..`, absolute paths, symlink escapes → a clean refusal dict, never the host filesystem.** Read-only: no write surface exists through A3 — belt-and-braces battery pin. Zero ring spend, counter-pinned.
- `command.py` — v1.5 rows (small, deliberate): "what did you learn today" → lessons digest · "what's in your brain" → honest tree summary · "read me my journal" / "read today's journal" → journal read-back (Cooper-gated where audience law applies). Closed Hinglish aliases declared (suggest `kya seekha`). **All zero-ring reads, counter-pinned.**
- `canon.py` — extend, generative + literal-pinned: `LINE_INNER_PRIVATE = "That's my own journal. Cooper's ears only."` · lessons/tree digest family (pin ≥3 literals against fixture trees) · consolidation-deferred line shape (honest silence is also lawful — declare which, pin accordingly).

## 2. Ring discipline + privacy (battery PROVES, never claims)
- ZERO-RING: browsing rows, A3 explorer, journal write — all local; counter-pinned.
- The ONLY ring spender is `consolidate()` at ≤2 smart calls/pass, pinned; every ring-bound slice is swept for inner-voice canary absence.
- Audience law on people/inner content: guest/family sessions get refusal lines, zero content bytes — re-uses the persona/guest machinery, battery-pinned.
- §29: the tree grows uncapped; watcher metering of `tars-brain/` size continues (visibility only — no enforcement branch anywhere near the brain).

## 3. Grammar v1.5 (append-only; 3 example utterances per row)
Rows: lessons digest · brain summary · journal read-back. Row-for-row exercised.

## 4. Crash, determinism, guards
- Crash child: SIGKILL mid-consolidation → reopen: no half-written brain file (atomic law — either the old bytes or the new), journal integrity, drill marker intact.
- urlopen/subprocess patched-RAISE extended over brain.py.
- All 540 prior checks byte-stable except §7. Determinism ×2. Expect ≈595–615.

## 5. Agent-log (one append-only entry)
What shipped · tree shape + consolidation cap rationale · machine-taught fixes in the open · acceptance CORRECTION for P-CORE-9: "PASS, banked by Architect audit Aug-20 atop 8240333 — 540/540 re-run twice, drill confession once-first-LOCAL re-verified, §29 grep-law + warn-inclusive gauge math pinned, re-aim pair exactly the sanctioned one."

## 6. Deliverable + REPORT block (§3.5 shape — mandatory)
Whole files only · zero dead code · zero unused imports (documented re-export/presence-probe patterns recognized) · zero >U+2100 glyphs in code AND docstrings (the ③ lesson is now law) · zero new deps · zero network.
Commit: `[CORE] P-CORE-10 — Living Brain: tars-brain tree, daily journal, ring-bounded consolidation, Inner-Voice privacy, A3 explorer (list_brain/brain_text path-confined), grammar v1.5, <N>-check selftest`.
REPORT: FILES (line counts) · 7-LAWS RECITAL · SELFTEST OUTPUT (fresh-clone tail, twice) · CONTRACT CHECK (A3 served, channels closed, bus at 9) · KNOWN LIMITS · RE-AIMS · PUSHED (short hash, fresh-clone-verified green).

## 7. Sanctioned re-aims (the ONLY tolerated diffs; disclose in-code + REPORT)
1. If any pending pin names the A3 brain methods as unshipped — those leave the pending set (served now). Re-pin every still-pending neighbor byte-exact.
2. If persona/memory-assembly pins assumed journal-absence, name them and re-prove the protected law on the new vehicle. Nothing else moves.

**Never List + 7 Laws bind. §25.5 says it grows for life — nothing cages it, and nothing inside it ever betrays the house it grew in. The machine's truth over green lights. Grow the mind.**
