# 🚀 P0 BUILD PACKAGE — "tars-vault" (Replit)
**Aug 10, 2026 · Phase 0: the key ring + quota gauge. Machine-independent. ~20 min operator duty.**

## Operator's steps (phone or PC — Replit app/site)
1. Replit account → **New Repl → Python → name it `tars-vault`**
2. Paste the prompt between the ✂ lines into **Replit Agent** → let it build → click Run/ask it to verify all tests pass
3. **Secrets tab** (lock icon): add `GROQ_API_KEY_1` = a free key from console.groq.com (Google login → API Keys → Create). Slots 2-6 stay empty for now — the ring works with any count
4. Run the **5 acceptance tests** below → screenshot the `--table` output → **paste it back to the Architect**

⸻ ✂ COPY BELOW THIS LINE INTO REPLIT AGENT ✂ ⸻

Build a Python 3.11 project called "tars-vault" — the key-vault + quota-gauge module for a larger assistant system named TARS. **Stdlib only — zero pip installs** (must run on Replit, Windows, and Android Pydroid unchanged).

## Files to create

### 1. `keys.json` — the ring config + persona defaults
- `keys`: slots `key-1`…`key-6`; each maps to env var `GROQ_API_KEY_1`…`GROQ_API_KEY_6`
- `lanes`:
  - `fast` → model `llama-3.1-8b-instant` · limits 30 req/min, 14,400 req/day, 6,000 tok/min, 500,000 tok/day
  - `smart` → `llama-3.3-70b-versatile` (1,000 req/day, 100,000 tok/day) · `moonshotai/kimi-k2-instruct` · `openai/gpt-oss-120b`
  - `eyes` → `meta-llama/llama-4-scout-17b-16e-instruct`
  - `ears_backup` → `whisper-large-v3-turbo` (2,000 req/day)
  - `ultra` → external: OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free`, env var `OPENROUTER_API_KEY`
- `budgets`: `tokens_per_key_per_day: 250000` · `warn_at: 0.80`
- `persona`: `dials: {honesty: 90 (fixed: true), humor: 5, vernacular: 30, discretion: 95, trust: 25}` · `boot_line: "TARS online. Honesty: ninety. Humor: five. Vernacular: thirty."`

### 2. `usage_logger.py`
Append-only JSONL ledger `usage.jsonl`. One line per call: `timestamp, key_alias, lane, model, tokens_in, tokens_out, latency_ms`. Crash-safe (open-append-close every write; no buffered state).

### 3. `gauge.py` — the CLI
- `--table` → pretty table: per key × lane: requests used/limit today, tokens used/budget, status `OK` / `WARN ⚠️` (≥80%) / `OVER ❌` (≥100%)
- `--full` → same + avg/min/max latency
- `--next MODEL` → prints which key alias to use for that model: **sequential rotation that SKIPS keys at WARN or OVER for that model's lane**; clean friendly error for unknown model (no traceback)
- `--reset-demo` → clears the ledger to zeros
- **Privacy law:** env key VALUES are never printed — only `set`/`missing` per slot

### 4. `demo_seed.py`
Seeds `usage.jsonl` with fake history so warn/over/rotation behavior is provable on day one.

### 5. `README.md`
5 lines: what the ring is, where keys live (Replit Secrets), how rotation behaves, how to add key 2-6 later.

## Self-check before you report done
Run and show output: `python gauge.py --table` · `python demo_seed.py && python gauge.py --table` · `python gauge.py --next llama-3.1-8b-instant` with key-1 forced OVER · `python gauge.py --next banana` · `python gauge.py --reset-demo`.

⸻ ✂ COPY ABOVE THIS LINE ✂ ⸻

## Acceptance tests (Operator runs, pastes outputs)
| # | Command | Pass when |
|---|---|---|
| T0.1 | `python gauge.py --table` | 6 key rows × lanes render, all zeros |
| T0.2 | seed, force key-1 WARN + key-2 OVER on fast lane → `--next llama-3.1-8b-instant` | returns key-3 (skips both) |
| T0.3 | `--next banana` | clean error line, no traceback |
| T0.4 | eyeball every output | no real key characters anywhere |
| T0.5 | `--reset-demo` then `--table` | back to zeros |

**Paste back to Architect:** T0.2's full output + any Agent weirdness. Then P1 (the Soul) gets its prompt.

*P0 is where TARS's heartbeat starts. The machine arrives when it arrives — the soul doesn't wait for the body.* 🛰️
