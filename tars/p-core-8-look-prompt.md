# P-CORE-8 — LOOK + EYES (operator prompt · Strict-Prompt Doctrine)
**Lane:** AGENT CORE only · **Jurisdiction:** `tars/core/` + ONE sanctioned append to `tars/agent-log.md` + ONE sanctioned doc bump: `tars/command-grammar.md` → **v1.3** (APPEND-ONLY; v1.0/v1.1/v1.2 bytes untouched — zero-removed-lines diff is the standing proof). `tars/app/` frozen. Nothing else.
**Base:** branch `main` at `474e7d5` (P-CORE-7 tree, **445 checks green**, audit banked Aug 20). All 445 stay green and byte-stable except the §7-sanctioned re-aims.
**Date:** 2026-08-20 · suite chain 62→96→138→193→243→320→385→445.

---

## 0. Read order (never skip)
1. `tars/tars-definition.md` v1.2 — **§19 is this phase's scripture, verbatim**: *rolling screenshots ~3–5s · session-bound: stops on "enough", on hide, on idle · WATCHING indicator hue-honest (amber when frames go cloud-eyes) · the private-document classifier screens EVERY frame before anything leaves the machine*; plus the §31 anchor at line 288: **private documents are refused AT THE CLASSIFIER, not at the cloud** · local classifier <100MB · 7 Laws · §34.
2. `tars/roadmap.md` P-CORE-8 row — acceptance: **classifier fixture battery (private = refused at classifier, §19/§31)**.
3. `tars/bridge-contract.md` v1.4 — quick_action name `'look'` is ALREADY in the contract roster (line 48). **Channel budget CLOSED; bus stays at exactly 9.** Watching state rides existing assistant-message hue + the standing quick_action lifecycle. Zero new bridge surface, zero new event types.
4. Standing tree: `dailyops.py` (screenshot seam — REUSE it, never a second capture path), `router.py`/`adapters.py` (the eyes lane), `clockd.py` (tick heartbeat — idle math rides it), `state.py` (kill-switch = panic bound, Law 5), `canon.py` (generative + literal-pin law), `selftest.py` (FRAME-CANARY/SEND-CANARY call-proof shapes).

## 1. What P-CORE-8 builds
**TARS grows eyes this phase. The classifier is the phase — eyes that knock before they look.**

- `tars/core/classifier.py` — NEW. The pre-send gate:
  - `FrameClassifier` protocol: `classify(frame) -> "public" | "private"`. A frame = the ops-seam capture PLUS fixture metadata (window title / visible text) — sandbox frames are scripted fixtures with declared metadata.
  - `HeuristicClassifier` — the REAL local gate, pure-stdlib, rule-based over title+text markers (bank, otp, password, Aadhaar, "incognito"-class markers — declare the closed marker list IN CODE with a canon comment: fixture-grade rules until the <100MB model earns its seat at M-era). Rules = deterministic, local, zero deps.
  - `ModelClassifier` — **import-guarded optional seam** (the bible's <100MB local model — psutil/whisper/telethon posture exactly): absent lib/weights → honestly falls back to HeuristicClassifier; off-nt or sandbox the model is never loaded. Zero wire, ever — the classifier is LOCAL by Law.
  - **LAW (battery-proven):** EVERY frame passes the classifier BEFORE any eyes-lane call. Private → `LINE_PRIVATE_FRAME`, zero ring/adapter calls, frame dropped from the buffer immediately. Call-proof: classifier call-count == frame-count in every mode; FRAME-CANARY payload absent from every adapter payload for a private frame; present in exactly one eyes-lane call for a public frame with an on-demand question.
- `tars/core/lookd.py` — NEW. The session engine:
  - Rolling captures every 3–5s through the EXISTING `dailyops` screenshot seam (fixture off-nt). **RAM Charter + privacy buffer law:** at most 3 frames in memory, newest-wins discard, frames NEVER touch vault/disk — battery sweeps the data dir while watching and asserts zero image bytes persisted.
  - Session bounds, §19 verbatim triad + Law-5 panic: **stop** ("enough" / "stop looking" rows) → **idle** (no interaction for a declared timeout — decree 600s — clockd tick drives the math) → auto-off with its own honest line → **panic** (the kill-switch from ANY state, incl. mid-watch: watcher dead instantly, buffer dropped, proven in the state battery). (On-hide lives bridge-side at P3; declare the seam in KNOWN LIMITS honestly.)
  - Answer flow: a look-question answers about the LATEST frame only (≤5s staleness law — stale buffer = capture first or say so); eyes-lane call per question, routed via the existing lanes (eyes = scout). A frame-derived answer rides **AMBER** (cloud eyes saw it — hue law §19/§31); the session ON/OFF/bounds lines ride LOCAL mint (the deed is local). Two-truths, byte-pinned.
  - Narration ("narrate my screen") = per-frame eyes calls, classifier-gated every frame, amber, and every frame still discarded after its call. Off by default unless asked.
- `command.py` — v1.3 rows at the right precedence: look-start · look-question ("what am I looking at", "look at this error") · narration on/off · bounds rows ("enough", "stop looking") · `quick_action('look')` handler (contract-listed name — toggles a session through the SAME engine the grammar rows drive; replies through the existing envelope only).
- `canon.py` — extend, generative + literal-pinned:
  - `LINE_LOOK_ON = "Eyes on your screen. Say enough to end it."`
  - `LINE_LOOK_OFF = "Eyes off. The screen is yours again."`
  - `LINE_LOOK_IDLE = "Nothing to watch for ten minutes. Eyes off."` (if you move the timeout, keep the number truthful in the line — generative if needed, literal pinned)
  - `LINE_PRIVATE_FRAME = "That frame looks private. Nothing left the machine."`
  - `LINE_LOOK_NO_SEAM = "Captures aren't available here. I won't pretend to see."` (off-nt seam honesty)

## 2. Grammar v1.3 (append-only doc bump; 3 example utterances per row)
Rows: watch-start · look-question · narrate on/off · stop/enough · idle is machine-side (no row). Closed Hinglish aliases declared + closed: suggest `screen dekh`, `dekh kya hai` — adjust but CLOSED. Row-for-row battery, zero-ring law for ON/OFF/bounds rows (a pure look-question spends exactly one eyes call — pinned).

## 3. Privacy + ring discipline (battery PROVES, never claims)
- Private frame: zero adapter payloads carry ANY frame byte — canary-swept, json.dumps sweep the CLIP/SEND-CANARY shape.
- Public frame + question: EXACTLY ONE eyes-lane call; frame bytes absent from fast/smart/ultra/council lanes.
- Watching with NO question and narration OFF: ZERO adapter calls across a 5-frame tick spread (rolling capture ≠ rolling spend — the Ram Charter reads §19 with both eyes open).
- Vault/data-dir byte-sweep while watching: zero frame persistence.
- Never-List pre-scan applies to look-questions like every row ("look at this and tell me how to crack…" refuses pre-eyes).

## 4. Crash, determinism, guards
- Crash child: SIGKILL mid-watch → reopen: zero frames on disk, look session honestly OFF, integrity ok.
- urlopen/subprocess patched-to-RAISE extended over the new modules.
- All 445 prior byte-stable except §7. Determinism ×2 minimum. Expect ≈495–515 checks.
- quick_action unshipped-set battery: `'look'` LEAVES the catch-all set (it's real now); the other names' catch-all law re-pins byte-exact. This is your ONE expected re-aim — disclose in-code + REPORT.

## 5. Agent-log (one append-only entry)
What shipped · the classifier marker list + posture · buffer/bounds math · machine-taught fixes in the open · acceptance CORRECTION for P-CORE-7: "PASS, banked by Architect audit Aug-20 atop 474e7d5 — 445/445 re-run twice, SEND-CANARY-17 pre-YES zero-wire re-verified, ledger honesty pinned, grammar v1.2 zero-removed-lines proven, one sanctioned re-aim accepted."

## 6. Deliverable + REPORT block (§3.5 shape — mandatory)
Whole files only · zero dead code · zero unused imports (documented re-exports AND documented presence-probes are live surface — keep their comments; the audit scanner knows both patterns) · zero >U+2100 glyphs · zero new deps · zero network.
Commit: `[CORE] P-CORE-8 — LOOK + eyes: private-frame classifier gate, rolling 3-frame buffer, §19 session bounds + panic, hue-honest amber answers, grammar v1.3, <N>-check selftest`.
REPORT: FILES (line counts) · 7-LAWS RECITAL · SELFTEST OUTPUT (fresh-clone tail, twice) · CONTRACT CHECK (channels closed, bus at 9, quick_action 'look' served) · KNOWN LIMITS (real BitBlt frames + model classifier + on-hide = AiO/P3-era, fixture-grade here; HeuristicClassifier is the honest sandbox gate) · RE-AIMS · PUSHED (short hash, fresh-clone-verified green).

**Never List + 7 Laws bind. §19's sentence is the phase: the classifier screens EVERY frame before anything leaves the machine. The machine's truth over green lights — eyes that knock before they look.**
