# AGENT_LOG.md — the live build diary of TARS (Chain Protocol v1)
# This file is APPEND-ONLY. It is the memory chain between phases: every Replit Agent
# session reads this FIRST, before writing any code, together with TARS_KNOWLEDGE.md.
#
# RULES (Chain Protocol link 5):
#   R1. Read this file fully at session start.
#   R2. Never edit or rewrite existing entries. History is immutable.
#   R3. Corrections are NEW lines inside a new entry, prefixed "CORRECTION —".
#   R4. At phase end, append one entry in the EXACT template below, between the
#       marker lines "<!-- LOG-APPEND-BELOW -->" style usage: append AFTER the last entry.
#   R5. The commit that carries your entry must be pushed in the same session.
#
# ENTRY TEMPLATE (copy verbatim, fill every field; write "none" where empty):
# ---------------------------------------------------------------
# ## [PX] — <phase name> — <STATUS: PASSED|FAILED|PARTIAL> — <YYYY-MM-DD>
# - Built: <files created>
# - Modified: <existing files touched + WHY (must cite the phase prompt's integration point)>
# - Key facts for future phases: <functions, flags, formats, canon lines added>
# - Self-tests: <what ran, result counts>
# - Acceptance: <which acceptance tests Cooper passed, or "pending Cooper audit">
# - Deviations: <anything that diverged from the phase prompt, or "none">
# - Commit: <commit message used>
# ---------------------------------------------------------------

<!-- entries begin -->

## [P0] — Vault & Gauge — PASSED — 2026-08-10
- Built: keys.json, usage_logger.py, gauge.py, demo_seed.py, README.md, usage.jsonl (empty ledger; gitignored)
- Modified: none (first phase)
- Key facts for future phases: six Groq slots GROQ_API_KEY_1..6; lanes fast/smart/eyes/ears_backup/ultra; quotas in keys.json (fast 14,400/day, smart ~1,000/day, whisper 2,000/day); rotation via `python gauge.py --next <model>` SKIPS keys at WARN/OVER; `--table` prints set/missing env status only (never key chars); `--reset-demo` zeroes demo ledger. usage_logger.append() is the crash-safe spend writer every brain call must use.
- Self-tests: T0.1–T0.5 all green (Cooper screenshot-verified: key-1 OVER + key-2 WARN → --next returned key-3; "banana" gave friendly unknown-model error; demo reset to zeros; syntax compile passed)
- Acceptance: PASSED 5/5 by Cooper screenshots, 2026-08-10 21:11 IST (repl "Tars Vault", Replit Lite free tier)
- Deviations: none
- Commit: pre-GitHub era (P0 predates the repo); carried into the P1 first push

## [P1] — Soul (router + dials + honesty governor) — PASSED — 2026-08-10
- Built: soul.py (stdlib urllib Groq client, 30s timeout, retry-once via gauge rotation), selftest.py (8 offline router/dial checks). ALSO first-use protocol: private GitHub repo created via GITHUB_TOKEN secret; .gitignore shields .env, usage.jsonl, __pycache__/, *.pyc, .replit, replit.nix; all P0 files committed.
- Modified: none
- Key facts for future phases: router defaults to fast lane llama-3.1-8b-instant; smart lane llama-3.3-70b-versatile triggers on >120 chars or keywords (explain, derive, proof, why, solve, essay, physics, chemistry, maths, doubt, concept); "ultra:" prefix routes to OpenRouter nemotron-3-ultra with fallback line "Ultra lane needs its key. Fast lane it is."; replies tagged [fast]/[smart]/[ultra]; boot line "TARS online. Honesty: ninety. Humor: five. Vernacular: thirty." at startup; live dial commands ("humor 60" → "Humor adjusted to sixty percent."); honesty requests → "Honesty is fixed at ninety."; system prompt carries the four honesty clauses verbatim; loop prompts you>/tars>; "exit" → "Standing down."; every brain call passes through usage_logger.
- Self-tests: selftest.py 8/8 ALL PASS (offline, zero API calls)
- Acceptance: PASSED — Cooper-declared in chat, 2026-08-10 (transcripts filed by Cooper)
- Deviations: none
- Commit: "P1: soul.py + selftest + private repo setup" (repo: tars-vault, private)

## [SYS] — Chain Protocol v1 installed — 2026-08-10
- Built: TARS_KNOWLEDGE.md (v1.0), AGENT_LOG.md (this file)
- Modified: none
- Key facts for future phases: from this point every phase obeys the 7-link Chain Protocol (READ, DECLARE, BUILD, VERIFY, LOG, PUSH, REPORT). Knowledge is versioned; a phase prompt's REQUIRES line must match TARS_KNOWLEDGE.md VERSION or the agent stops and asks for the refresh pack.
- Self-tests: n/a (system installation)
- Acceptance: decreed by Cooper, 2026-08-10
- Deviations: none
- Commit: carried in the P2-A push

<!-- next entry appends below this line -->

## [P-CORE-0] — CORE lane · Skeleton + state machine (App-Era two-lane build) — PASSED — 2026-08-17
- Built: tars/core/__init__.py (package marker), canon.py (all bible §11 lines + dial-ack/confirm composers), logx.py (logs.jsonl append-only fsync'd), settings.py (5 dials, honesty hard-locked, atomic saves), vault.py (vault.db WAL crash-safe: kv/memory/ledger), bus.py (8 contract event types, fault-isolated), state.py (bible §32 machine + StateNotice single emit path), __main__.py (`python -m tars.core --demochat` headless demo + Printer transport), selftest.py (62-check proof incl. SIGKILL-mid-write child)
- Modified: tars/agent-log.md (this entry, per bridge-contract §1 Chain Protocol [CORE] tag — Deployment: repo TARS, deploy-key auth per roadmap §2)
- Key facts for future phases: data dir = TARS_DATA env or ~/.tars (M-1 wires C:\TARS); StateNotice keys exactly {state,dials,audience,lane,hue} with state tokens lowercase (off/armed/listening/thinking/speaking/error) — APP maps to labels at merge; machine mic_open is a pure function of state (true only in LISTENING); set_dial("honesty",…) returns {"ok": false, "line": "Honesty is fixed at ninety."} byte-exact; bad dial inputs return the canon catch-all; kill() from any state emits the 'close' event reason "kill-switch"; ERROR path: fail(cause) → recover() yields prior state; vault honesty note: memory/ledger strictly INSERT-only, kv upserts (WAL gives both crash-safety); audience static "cooper" until Cooper ID (P-CORE-4); lane null until router (P-CORE-1).
- Self-tests: `python -m tars.core.selftest` → ALL GREEN (62/62): 13 canon byte-exact, 13 settings/vault/logx functional, 21 state machine + bus (incl. all 8 contract events through Printer), 9 demochat (2 runs + real CLI), 6 crash-kill — child SIGKILLed mid-burst after 6,052 memory commits / 6,051 log lines: integrity=ok, kv 5/5, zero corruption on re-open.
- Acceptance: pending Cooper audit (REPORT block delivered to Delivery with verbatim selftest stdout)
- Deviations: none (phase boundary respected: no router, audio, operator verbs, or pywebview)
- Commit: "[CORE] P-CORE-0 — skeleton + state machine: canon, dials, crash-safe vault/logs, bridge bus, headless demochat, SIGKILL-proof selftest"

## [P-CORE-1] — CORE lane · Brain ring (8-key quota ring, mocked adapters) — PASSED — 2026-08-17
- Built: tars/core/keys.py (ring loader: caller-provided env/.env mapping, slot-stable indexes 1–8, midnight rollover via injectable clock, key strings repr-sealed), adapters.py (GroqAdapter/OpenRouterAdapter with byte-exact endpoints + 30s ceiling; no keys → refusal dict, never the wire; FixtureAdapter scripted twin), router.py (3-gate router: council/ultra named-only, length>120 or keyword → smart, else fast; ring walk with canon mid-fail line and all-spent drain; threaded council with writer lock), gauge.py (contract §4 keys[] rows; council quota note), ring_demo.py (`python -m tars.core.ring_demo` fixture tour), selftest.py replaced whole (96 checks)
- Modified: tars/core/vault.py (+ledger_tail for the demo's audit trail; sqlite check_same_thread=False so council worker threads can ledger under the router's single writer lock — integration point: router.py._single); tars/agent-log.md (this entry). CORRECTION — P-CORE-0 entry's Acceptance now reads: PASS (Architect re-ran the selftest directly, 62/62 green, audit banked in commit 9369f12).
- Key facts for future phases: Router(ring, {provider: adapter}, vault, bus).route(text) -> {ok, text, lane, key_visible_name, hue, tokens, notices, warn} (+note/votes for council); Router.gate(text) is the pure 3-gate; warn rule DECLARED: remainingPct ≤ 20 renders warn (INCLUSIVE — demo scene 8), 0 = spent; mid-fail line = "That brain didn't answer. Trying another key." per faulted key, drained ring (every key spent/failed) = "All keys are spent. Standing by until reset."; a faulted key sits out until midnight rollover; budgets are requests/day per LANE_CAPS (fast 14400, smart 1000, eyes 14400, ears 2000, ultra/council 50); KeyState.visible_name = "groq#3" style — never key chars; LANE_MODELS OpenRouter slugs carry bible §26 names pending M-1 console confirmation; hue is 'cloud' on every brain reply by construction.
- Self-tests: `python -m tars.core.selftest` → ALL GREEN (96/96): P-CORE-0's 62 preserved (canon 13 · functional 14 · machine+bus 21 · demochat 9 · crash-kill 6 — SIGKILL mid-burst, 6,133 memory rows / 6,133 log lines, zero corruption) + ring battery 34: rotation groq#1..#6 · at-budget skip without a failing call · drained canon byte-exact · timeout/429/5xx/garbage retry-once · long-and-keyword → smart · named ultra → openrouter#7 · council 3 votes / 3 ledger entries / tokens 10+20+30 exact · clock-injected midnight rollover (ledger untouched) · gauge §4 shape + inclusive warn boundary · twice-identical determinism battery · no-keys refusal dict · byte-exact endpoints · ring_demo CLI substring battery.
- Acceptance: pending Cooper audit (REPORT block delivered to Delivery with verbatim selftest stdout)
- Deviations: none (fixtures only — zero network in sandbox, by decree and by design)
- Commit: "[CORE] P-CORE-1 — brain ring: 8-key rotation, 3-gate router, mocked adapters, gauge rows, canon fail lines, 96-check selftest"

## [P-CORE-2] — CORE lane · Persona + memory (the soul takes shape) — PASSED — 2026-08-18
- Built: tars/core/persona.py (byte-stable system-prompt builder: identity / §12 honesty clauses VERBATIM / live dials with pinned §10-anchor bands / audience gate / memory block cooper-only / behavior law), dialog.py (the conversation service: send() turn driver, chats+messages persisted, ChatSummary/ChatMessage contract shapes, dial+remember+brain intent order, A1 read_aloud intake & redo regeneration, A2 done-shape), selftest.py extended to 138 checks
- Modified: canon.py (+3 ARCHITECT-DRAFTED lines LINE_NOTED/LINE_GUEST/LINE_GUEST_DIAL, pending Cooper veto); state.py (+audience property, set_audience with tier validation); vault.py (+chats/messages tables & primitives; the ONLY update ever issued is message_mark_superseded); router.py (whole-file reship: optional system_prompt/history thread into every call, council seats included; P-CORE-1 behavior byte-identical); adapters.py (FixtureAdapter records received messages; AdapterResult contract unchanged); tars/agent-log.md (this entry)
- Key facts for future phases: Dialog(settings, vault, router, machine, bus) — send(text)->{chatId}; quick_action('read_aloud'|'redo', {chatId,messageId}); done events carry exactly {chatId,messageId,hue,lane} (A2); chunk.seq restarts per message until streaming lands; memory block header "What you remember (local vault):" appears ONLY for cooper with non-empty memories (else omitted, never emptied); dial gate: audience != cooper -> "Only Cooper moves the dials."; remember-intents cooper-only by declared fall-through (no canon refusal exists); superseded=own-id self-flag on the prior answer, replacement is a fresh row, open_chat shows visible rows only; speak intake is kv key "speak_request:<mid>"="queued" (P-CORE-3 drains); Machine.set_audience(cooper|family|guest) + .audience property; persona.HONESTY_CLAUSES is the single §12 source — never reword.
- Self-tests: `python -m tars.core.selftest` → ALL GREEN (138/138): prior 96 preserved byte-for-byte (incl. demochat replays + SIGKILL crash-kill, now covering chats/messages: 3,642 rows, zero corruption) + persona battery 42: §12 clauses on fast/smart/all-3-council-seat calls (fixture-RECEIVED) · humor 5 vs 60 directive bytes · typed honesty refusal · memory round-trip (LINE_NOTED → next prompt carries the fact) · guest: block OMITTED + LINE_GUEST_DIAL + no vault writes · family identical minus memories · read_aloud good/bad id · redo supersedes-self + fresh messageId in done · A2 exact done-keys · 10-message sliding window proof · determinism double-build.
- Acceptance: pending Cooper/Architect audit (REPORT block delivered to Delivery with verbatim selftest stdout)
- Deviations: superseded marks the PRIOR row with its own id (literal spec reading), replacement carries NULL — declared; quick_action returns contract-superset dicts ({ok, chatId, …}) — declared; v1.4 skin absorbed, CORE ships no colors.
- Commit: "[CORE] P-CORE-2 — persona + memory: system-prompt builder (§12 verbatim, live dials), dialog service, memory flows, guest register, A1/A2 paid, 138-check selftest"
