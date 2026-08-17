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
