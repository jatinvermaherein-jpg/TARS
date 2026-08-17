# TARS — PHASE 1 BUILD DIRECTIVE: "The Soul"
**This document is the complete instruction set for the Replit Agent. Execute top to bottom. The human operator will run acceptance checks afterwards — build so they pass. Stdlib Python only, no pip, and NEVER print or commit any secret value.**

---

## A. Project context (what already exists)
This Repl (`tars-vault`) already contains a WORKING vault from Phase 0: `keys.json` (6 Groq key slots, lanes, quotas, budgets, persona dials), `usage_logger.py` (append-only JSONL ledger), `gauge.py` (rotation CLI), `demo_seed.py`, `usage.jsonl`, `README.md`. **Do not break or rewrite them — you are extending, not rebuilding.**

## B. First-time GitHub setup (do this FIRST)
1. The operator has placed a GitHub personal access token in Replit Secrets as `GITHUB_TOKEN`. If missing, STOP and ask the operator for it — never invent one.
2. Create a new **private** repo on the operator's account via API, e.g.:
   `curl -s -H "Authorization: token $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" https://api.github.com/user/repos -d '{"name":"tars-vault","private":true}'`
   Read the account login from `https://api.github.com/user`.
3. Create `.gitignore` containing exactly: `.env`, `usage.jsonl`, `__pycache__/`, `*.pyc`, `.replit`, `replit.nix` — **secrets and the usage ledger never leave the machine.** `keys.json` contains NO secret values (env-var names only) so it commits safely.
4. `git init` if needed, set remote with the token-authenticated URL, commit EVERYTHING from Phase 0 (message: `P0: vault & gauge`), push to `main`. Print the repo URL when done.

## C. Build `soul.py` — chat loop with 3-gate routing, dials, honesty governor

### C1. Groq client (urllib only)
- POST `https://api.groq.com/openai/v1/chat/completions` with messages = system prompt + user turn, model per lane.
- Key selection: run `python gauge.py --next MODEL`, parse the alias, map alias → env var (key-3 → `GROQ_API_KEY_3`); if that env is missing, walk forward through slots until a set key is found.
- Timeout 30s. On 429/5xx/timeout: log via usage_logger, print exactly `That brain didn't answer. Trying another key.` and retry ONCE with the next key. Second failure: print `Something went wrong. TARS is still here.` and keep the loop alive.

### C2. Router (pure function `route(text) -> lane`, independently importable/testable)
- Default **fast** → `llama-3.1-8b-instant`
- **smart** → `llama-3.3-70b-versatile` when: len > 120 chars, or contains any of (case-insensitive): `explain, derive, proof, why, solve, essay, physics, chemistry, maths, doubt, concept`
- **ultra** only when text starts with `ultra:` → strip the prefix; if `OPENROUTER_API_KEY` missing → reply exactly `Ultra lane needs its key. Fast lane it is.` and use fast. No crash ever.
- Replies carry a tag: `[fast]` / `[smart]` / `[ultra]`.

### C3. Dials (persona engine)
- Load `persona` from keys.json: `honesty:90 fixed, humor:5, vernacular:30, discretion:95, trust:25`.
- Accept dial commands as `humor 60` or `TARS, humor 60` (all four non-honesty dials, 0–100) → update in-memory + confirm like `Humor adjusted to sixty percent.` Any honesty change → `Honesty is fixed at ninety.`
- Startup prints the full boot line from keys.json.
- System prompt is BUILT from dial values: humor <20 → strictly formal; ≥60 → dry one-liners permitted. vernacular ≥50 → light Hinglish seasoning permitted. And it MUST contain these clauses verbatim in every state: `Never flatter. If you do not know, say you do not know. Never invent facts, numbers, citations, or sources. When uncertain, say what part you are unsure of.`

### C4. Loop & logging
- `python soul.py` → `you> ` input, replies at `tars> ` with routing tag; `exit` prints `Standing down.` and quits cleanly.
- Log EVERY call through `usage_logger` (lane, model, tokens from API `usage`, measured latency).

### C5. Forbidden in this phase
No pip · no extra files beyond `soul.py` + `selftest.py` (and git files) · no chat persistence/memory · no printing of key values.

## D. Build `selftest.py` (zero API calls)
Print PASS/FAIL lines: (a) router decisions on 8 canned strings — `hi` → fast; a >120-char "explain the doppler effect…" → smart; `ultra: test` → ultra-fallback path (no key present) resolves to fast with the exact fallback line configured; a dial command like `TARS, humor 60` is NOT routed to any model; (b) dial parsing incl. honesty-fixed rejection; (c) system prompt at humor=5 contains all four honesty clauses and formal mode, at humor=90 permits dry wit. End with `ALL PASS` or a failure list.

## E. Final step — push to GitHub (STANDING RULE — every phase ends this way)
1. If `GITHUB_TOKEN` setup (Section B) was done, just commit: `soul.py`, `selftest.py`, any README note (message: `P1: soul — router, dials, honesty governor`).
2. `git push`. Confirm success by printing the latest commit URL/summary.
3. If the push fails, say so plainly and show the error — never fake success (Honesty 90 applies to builds too).

## F. Report back to the operator
Print: files created/modified · the GitHub repo URL + commit message(s) · selftest output · one example live exchange transcript (if a valid GROQ key was present) — or a clear note that live tests await a key.

---
*Phase 1 of 9 · TARS build line · The vault has a heartbeat; now it gets judgment.*
