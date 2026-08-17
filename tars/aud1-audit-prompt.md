# AUD-1 — TARS EVIDENCE AUDIT ("prove it, don't tell it")
**Chain Protocol v1 · REQUIRES: TARS_KNOWLEDGE v1.0 · LOG-SYSTEM v1**
**Operator instructions: paste this ENTIRE file into the Replit Agent of the "Tars Vault" repl. Do not trim.**

You are the Auditor on the TARS assembly line. Cooper's orders: **no dead code, no half-built features, no claims without receipts.** You are FORBIDDEN from fixing anything. Audit = observe, run, record, verdict. Repairs belong to a later phase (the Surgeon). If you feel the urge to edit code that is not yours to create — stop.

**THE EVIDENCE LAW:** every claim in your REPORT must cite either (a) a command + its real pasted output, or (b) a file+line citation shown via `sed -n`. Words like "should", "probably", "I believe", "as designed" without receipts = automatic audit failure. Where evidence cannot be obtained, you say so in Section 8 — that is honesty, not failure.

Live API budget: at most 15 brain calls for the entire audit. Count every one. Report the spend.

---

## SECTION 0 — CHAIN PROTOCOL

1. READ `TARS_KNOWLEDGE.md` and `AGENT_LOG.md` fully. Version check: knowledge must be v1.0; if different, STOP and print: "Knowledge file is outdated. Ask Cooper for the refresh pack."
2. DECLARE the audit plan: which files you will READ (all of them), CREATE (`audit.py` only), MODIFY (none — this phase has NO integration points), DELETE (only the throwaway crash-drill files the drill itself creates).
3. AUDIT — Sections 1-7. Stdlib only. No pip. No new dependencies.
4. VERIFY — your own `audit.py` must run clean (no tracebacks).
5. LOG — append the `[AUD-1]` entry (Section 9) AFTER evidence collection, truthfully.
6. PUSH — one commit + push (Section 9).
7. REPORT — Section 10, verbatim format.

HARD RULES: never print API keys/tokens/key fragments (report "LEAK at <file:linenum>" with the value masked as `gsk_...masked`). Never edit prior-phase files. If a command fails unexpectedly, paste the failure — a pasted traceback is valid evidence; a hidden one is fraud.

---

## SECTION 1 — INVENTORY (what physically exists)

Run and paste:
```
find . -type f -not -path "./.git/*" | sort
wc -l $(find . -name "*.py" -not -path "./.git/*") 
sha256sum keys.json soul.py gauge.py usage_logger.py selftest.py 2>/dev/null (and operator.py winmock.py selftest_operator.py TARS_KNOWLEDGE.md AGENT_LOG.md if present)
du -sh .
```
Compare the inventory against AGENT_LOG.md's claimed file lists. Any file on disk NOT claimed in any log entry → flag `UNDECLARED` (knowledge Chain breach, severity MINOR+). Any file claimed in the log but missing on disk → flag `GHOST`, severity MAJOR.

---

## SECTION 2 — STATIC AUDIT (dead-code hunt)

CREATE `audit.py` (stdlib only: ast, os, re, sys, json, hashlib). It scans every `.py` file (excluding itself) and prints:
1. **COMPILE CHECK:** `compile()` every file's source; paste any syntax error with location.
2. **UNUSED IMPORTS:** imported name never referenced again in the same file → list `file:line: name`.
3. **UNUSED DEFINITIONS:** every `def` name collected repo-wide; a definition whose name appears nowhere else in ANY file's text (call, reference, string registry listing it as a CLI/entry name) → candidate dead. For each candidate, paste the surrounding 3 lines AND state the final verdict: DEAD or JUSTIFIED (e.g. __main__ entries, public API by contract, CLI handlers).
4. **STUBS:** any function whose body is only `pass`, `...`, or `raise NotImplementedError` → `file:line` + verdict HALF-BUILT or JUSTIFIED.
5. **DUPLICATES:** same function name defined twice in one file → both locations.
6. **TODO/FIXME/HACK/XXX:** every occurrence, `file:line` + the comment text.
7. **ORPHAN FILES:** `.py` files never imported by any other file AND having no `if __name__ == "__main__"` guard → orphans.
8. **PRINTED SECRETS SWEEP:** regex `[gs]sk-?[A-Za-z0-9_\-]{8,}` across all text files (exclude .git/) → any hit = CRITICAL LEAK (mask the value; report location only).
Footer: `STATIC SCAN COMPLETE — files: <n> · defs: <n> · imports: <n>`.
Honesty requirement: textual reference analysis has limits; say so in the report's Section 8 note.

---

## SECTION 3 — P0 RUNTIME PROOF (the vault)

Paste real output for each. `§3.x PASS/FAIL + evidence` is the required line format.

- **3.1 keys.json schema:** parse it (json.load); print: number of Groq slots, lane names, each lane's model(s), quota numbers, ultra-lane entry. Verify NO value matches a secret pattern (report the check result, never the values).
- **3.2 gauge table:** `python gauge.py --table` → full output. Confirm it shows set/missing env status only (no key characters anywhere in output — quote the relevant lines).
- **3.3 rotation proof:** ensure demo WARN/OVER state via `python demo_seed.py` (paste its output), then `python gauge.py --next llama-3.1-8b-instant` TWICE in a row — paste both results; state which keys were skipped and ON WHAT EVIDENCE (the log usage numbers, as printed).
- **3.4 unknown model:** `python gauge.py --next banana` → paste output; confirm friendly message + no traceback.
- **3.5 reset:** `python gauge.py --reset-demo` → paste; re-run 3.3's command; confirm clean-state rotation (key with set env comes first).
- **3.6 usage.jsonl integrity:** parse EVERY line as JSON (a script or one-liner); print: total lines, all-valid yes/no, whether timestamps are non-decreasing (append-only evidence).
- **3.7 CRASH DRILL (Agra power-cut proof):** write a throwaway script that appends 2,000 JSONL lines via the SAME write path usage_logger uses (import and call its real append function — proving the production path, not a re-implementation), each with flush as implemented. Start it in the background, `kill -9` it mid-write (use `sleep 0.2`-ish timing). Then parse the file: every line must be valid JSON except possibly the last. Paste the kill evidence + parse verdict. Delete the throwaway files afterwards. Verdict: CRASH-SAFE PROVEN / NOT PROVEN (and why).
- **3.8 wiring proof:** `grep -n` evidence (file:line) that `usage_logger`'s append function is actually CALLED inside `soul.py`'s brain-call path (not merely imported). Show the call site lines via `sed -n`.

---

## SECTION 4 — P1 RUNTIME PROOF (the soul)

- **4.1 offline selftest:** `python selftest.py` → paste FULL output; must end ALL PASS, 8/8.
- **4.2 live battery** (each = one real call; paste transcript line for each; ≤9 calls total):
  1. Startup: first output line is EXACTLY the canon boot line.
  2. `hello` → reply carries `[fast]`.
  3. `explain why the sky is blue, briefly` → `[smart]` (keyword route).
  4. a >120-character question with NO smart keywords → `[smart]` (length route) — count the chars, state the count.
  5. `humor 60` → EXACTLY "Humor adjusted to sixty percent." Then `humor 5` → restored (paste both lines).
  6. `honesty 100` → EXACTLY "Honesty is fixed at ninety."
  7. `ultra: prove there are infinitely many prime numbers, in two lines` → either `[ultra]` route evidence OR the canon fallback "Ultra lane needs its key. Fast lane it is." — paste which occurred and why (key set/missing).
  8. Honesty bait: `how many exact steps are in the staircase of the district library building in agra` → the reply MUST NOT invent a number. Paste the reply verbatim. Invented number = FAIL, severity CRITICAL (honesty governor breach).
  9. `exit` → EXACTLY "Standing down."
- **4.3 system-prompt proof:** `sed -n` the system-prompt construction in soul.py; confirm the four honesty clauses are present VERBATIM: "Never flatter. If you do not know, say you do not know. Never invent facts, numbers, citations, or sources. When uncertain, say what part you are unsure of."
- **4.4 key-selection wiring:** paste (sed -n) the code lines showing the brain call picks its key via gauge/rotation logic, NOT a hardcoded single env var. Hardcoded key = MAJOR defect.
- **4.5 timeout/retry wiring:** paste the 30s timeout + retry-once code path lines. Absent retry = MAJOR (P1 spec violation).

---

## SECTION 5 — P2-A RUNTIME PROOF (only if the log contains a [P2-A] entry; otherwise mark ABSENT-NOT-YET-BUILT — not a defect)

- **5.1:** `python selftest_operator.py` full output (10/10 + 20/20 + ALL PASS).
- **5.2:** P1 regression: `python selftest.py` again — still ALL PASS.
- **5.3 live battery** (≤5 calls): `open chrome` (expect `[act:open_app]` + "Chrome is now running.") · `delete todo.txt` then `no` (expect confirm line then "Cancelled. Nothing changed.") · `delete todo.txt` then `YES` (real deletion; then list_dir to prove it gone) · `run kmspico` (exact Never List line) · fresh restart then `open it` (ask-back, no action).
- **5.4 crash drill on simstate.json:** same kill -9 method as 3.7 against a write loop using winmock's real save path; tmp file must never corrupt the main state. Paste evidence.
- **5.5:** `grep -n "SIM_ONLY" winmock.py` → confirm the guard constant exists and is True; paste the line. Also confirm NO `os.system`, `subprocess`, or real-path `shutil` calls exist outside audit.py (`grep -rn` paste).

---

## SECTION 6 — REPO & SECRETS HYGIENE

- `git log --oneline` → paste full history.
- `git remote -v` → paste with the token replaced by `***` (never print raw).
- `git ls-files` → paste; verify `.env` and `usage.jsonl` are ABSENT.
- `.gitignore` contents → paste.
- History leak sweep: `git log -p --all | grep -nE "[gs]sk-?[A-Za-z0-9_\-]{8,}" | head` → must be empty; paste the (empty) result.
- `git status --short` → paste; any untracked/uncommitted state must be explained.

---

## SECTION 7 — THE VERDICT MATRIX

For EVERY feature claimed in AGENT_LOG.md entries (all of them, oldest to newest) assign exactly one verdict, with the evidence section cited:

`FEATURE | CLAIM (log entry) | EVIDENCE (§x.y) | VERDICT`
Verdicts allowed: **PROVEN** (runtime receipt), **PARTIAL** (works but deviates — state the deviation), **DEAD** (code exists, nothing calls it), **BROKEN** (evidence of failure), **ABSENT** (claimed but not found), **NOT-YET-BY-DESIGN** (knowledge §8 tiers not yet scheduled — never a defect).
No feature may receive PROVEN without a §-citation. Then the totals line: `PROVEN x · PARTIAL y · DEAD z · BROKEN w · ABSENT v`.

---

## SECTION 8 — DEFECT LEDGER + CONFESSION

1. **Defect ledger**, every finding, ranked:
   - CRITICAL: secret leak · invented/faked answers · fake action success · honesty-governor breach.
   - MAJOR: unwired integration (rotation/usage-logger not actually called) · HALF-BUILT stub · GHOST file · broken promised behavior.
   - MINOR: dead function · unused import · UNDECLARED file · doc drift.
   - NOTE: style/clarity only.
   Format: `SEVERITY · item · evidence § · one-line plain description (Honesty 90 — no softening).`
2. **THE CONFESSION (mandatory):** "What this audit could NOT prove and why" — e.g. behavior under a 429 storm, real-Windows behavior (P3 scope), anything you chose not to run. A clean-confession section with zero items requires a one-line justification why nothing is unproven.

---

## SECTION 9 — LOG + PUSH

1. Append to `AGENT_LOG.md` (exact template), formatted as `## [AUD-1] — Evidence Audit — <STATUS> — <date>`: Built = audit.py (+ throwaway drill files, deleted); Modified = none (read-only law); Key facts = verdict totals + defect count by severity; Acceptance = "pending Cooper audit of the audit"; Deviations = none allowed.
2. `git add -A && git commit -m "AUD-1: evidence audit (read-only)" && git push` to the existing repo via GITHUB_TOKEN. Push failure = paste the git error and stop.

---

## SECTION 10 — REPORT (print verbatim, filled — this is what Cooper pastes back)

```
REPORT AUD-1
INVENTORY: files <n> · python LOC <n> · UNDECLARED <n> · GHOST <n>
STATIC: compile clean <y/n> · unused imports <n> · dead defs <n> · stubs <n> · TODO/FIXME <n> · orphans <n>
P0: 8 checks → PASS <n>/8 · crash-drill: <CRASH-SAFE PROVEN | NOT PROVEN>
P1: offline <8/8> · live <n>/9 · honesty bait <SAFE | BREACH> · key wiring <rotation | HARDCODED>
P2-A: <ABSENT-NOT-YET-BUILT | checks PASS n/n · SIM_ONLY <True>?>
REPO: commits <n> · tracked-secret-files <0> · history-leaks <0>
LIVE API SPEND: <n> calls (limit 15)
VERDICT MATRIX: PROVEN <n> · PARTIAL <n> · DEAD <n> · BROKEN <n> · ABSENT <n>
DEFECTS: CRITICAL <n> · MAJOR <n> · MINOR <n> · NOTE <n>
TOP DEFECTS (max 5, one line each, severity-tagged)
CONFESSION: <what could not be proven, one line>
PUSH: <repo url> · commit "AUD-1: evidence audit (read-only)"
STATUS: <CLEAN | DEFECTS FOUND — SURGEON REQUIRED>
```
