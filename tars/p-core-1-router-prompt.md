# P-CORE-1 — THE BRAIN RING (CORE lane · build prompt)
**Paste to AGENT CORE after P-CORE-0 PASS. Re-read order: bible v1.1 §26 · contract v1.1 · roadmap §3 + §6 · bridge-demo-script.md.**

---

Continuing AGENT CORE in the same repo (`git pull` first — contract is v1.1, demo-script v1.0 exists). Jurisdiction: `tars/core/` only (+ append-only `tars/agent-log.md`). This phase builds the **8-key quota ring with FULLY MOCKED adapters** — real keys never enter a sandbox (roadmap §4: first live call is the P3 ceremony on the AiO). Python 3.12, **stdlib only** (urllib for adapters' real codepath; it is written but never network-called here).

**SHIP (whole files, zero dead code):**
1. `tars/core/keys.py` — the ring loader: reads up to `GROQ_KEY_1..6` / `OPENROUTER_KEY_1..2` from env/`.env`-style file provided by the caller (never auto-reads; the host wires it) · every entry gets a KeyState {provider, index, spent_today, budget_pct, lane_seen} · midnight-reset rollover (local date flip clears counters) · **mock key set for testing**: caller passes synthetic key strings.
2. `tars/core/adapters.py` — two adapter classes with byte-exact request signatures for Groq chat-completions and OpenRouter chat-completions (model=lane map from bible §26: fast llama-3.1-8b-instant · smart llama-3.3-70b-versatile with alts kimi-k2/gpt-oss-120b · ultra nemotron-ultra on OR :free · council-spare OR free) each exposing `call(messages, **kw) -> AdapterResult{text, tokens, latency_ms, key_visible_name}` · a **FixtureAdapter** implementing the same interface from recorded fixtures (the ONLY adapter selftest uses) · failure injection hooks: {timeout, http_429, http_5xx, garbage_json}.
3. `tars/core/router.py` — the 3-gate router (bible §26): default = fast · escalate to smart on length>threshold OR complexity keywords (list lives in one constant, documented) · ultra/council ONLY when named in the command (e.g. "council on this", "ultra…") · **30s timeout → retry-once on the next healthy key → if every key for the lane is spent/failed: the §11 canon line** ("That brain didn't answer. Trying another key." mid-fail; "All keys are spent. Standing by until reset." when drained) · every call ledgered to vault.ledger {ts, lane, keyindex, tokens} · **80% budget warning returns a warn flag the caller can surface** · reply dict carries lane + key_visible_name (hue = 'cloud' always for brain calls).
4. `tars/core/gauge.py` — derives the StatusReport `keys[]` shape (contract §4) from KeyState: per-key remainingPct + state (ok / warn ≤20% / spent) · council arithmetic helper: council costs N parallel calls = N× ledger entries, one line in the reply 「council of 3 — 3x quota」style (plain text, no emoji).
5. `tars/core/selftest.py` — REPLACE the whole file (previous 62 checks must stay green) adding the P-CORE-1 battery:
   - rotation order across 6 Groq keys round-robin
   - a key AT budget is skipped without a failing call
   - all-keys-spent → canon line byte-exact, zero exceptions raised
   - timeout → canon line on first FAILING lane key, retry-once succeeds on next key (fixtures scripted)
   - 429 → retry-once path; 5xx → retry-once path; garbage JSON → treated as failure, not crash
   - gate arithmetic: long message routes to smart even when fast is healthy · "council on this" fires N=3 parallel fixture calls and ledger shows 3 entries · "ultra" named routes to OR-ultra fixture
   - ledger arithmetic exact (token sums), midnight-rollover test by clock injection
   - gauge shape = contract §4 keys[] exact; warn at 20% boundary inclusive/exclusive per your declared rule (state it)
   - determinism: fixture battery runs twice, identical outputs
6. `tars/core/ring_demo.py` — `--ringdemo` CLI: scripted tour (fast call → smart escalation → all-spent → council ×3) printing every routing decision + ledger tail; fixtures only.

**FORBIDDEN:** real network calls in selftest/demo (assert: adapter real-codepath exists but is unreachable without keys — prove by calling with no keys and getting the canon no-keys/refusal dict, not a crash) · emoji · TODOs · touching `tars/app/` · new dependencies · placeholder gauges.

**REPORT:** §3.5 block verbatim; commit `[CORE] P-CORE-1 …`.
