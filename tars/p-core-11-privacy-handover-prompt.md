# P-CORE-11 — PRIVACY NET + THE HANDOVER FAREWELL (operator prompt · Strict-Prompt Doctrine)
**Lane:** AGENT CORE only · **Jurisdiction:** `tars/core/` + ONE sanctioned append to `tars/agent-log.md` + ONE sanctioned doc bump: `tars/command-grammar.md` → **v1.6** (APPEND-ONLY; v1.0–v1.5 bytes untouched). `tars/app/` frozen. Nothing else.
**Base:** branch `main` at `24ada40` (P-CORE-10 tree, **595 checks green**, audit banked Aug 21). All 595 stay green and byte-stable except the §7-sanctioned re-aims.
**Date:** 2026-08-21 · suite chain …→385→445→495→540→595.

---

## 0. Read order (never skip)
1. `tars/tars-definition.md` v1.2 — **PART IX (the built-in farewell) read twice**: triple-gate = verified Cooper voice → spoken passphrase → typed `CONFIRM` → **10-second ABORTABLE countdown** · wipes voiceprints, vault, dials, personal logs, passphrase · **ASKS about the API keys** · keeps the app, the laws, the Never List — *house rules aren't memories* · Windows + user files 100% untouched · exactly ONE log line survives: `Handover executed <date>` · first boot after: *"Factory state. New commander, identify yourself. Honesty: ninety. Humor: five."* · plus the §30 ledger table (lines 271-278: what lives where, what Handover does to it) · §31 audience law · line 230 (people profiles wiped at Handover).
2. `tars/roadmap.md` P-CORE-11 row — acceptance: **wipe selftest: only `Handover executed <date>` survives; factory boot line**.
3. Standing tree: `voiceid.py` (tier verification + passphrase hash flow — REUSE, never fork) · `state.py` (kill-switch Law 5) · `vault.py` (`sent_log`, memory, journal rows) · `brain.py` (the tree that must die with its commander) · `settings.py` (dials, honesty fixed 90) · `logx.py` (the one surviving line) · `canon.py` · `command.py` gate machinery.

## 1. What P-CORE-11 builds
**The last thing TARS does for Cooper is leave cleanly. The farewell is the phase.**

- `tars/core/handover.py` — NEW. The farewell engine:
  - **Gate flow (grammar row `"tars handover"` — closed, NO Hinglish alias this time; declare it deliberately):**
    1. **Voice gate:** only a VERIFIED Cooper-tier voice opens the flow — family/guest `LINE_HANDOVER_VOICE_ONLY` and the flow never starts. (Standing voiceid tier law, battery-pinned at every tier.)
    2. **Passphrase gate:** spoken passphrase verified via the standing hash flow (`salt:sha256`, never stored in clear) — reuses voiceid.py, zero duplication.
    3. **Typed gate:** `LINE_HANDOVER_CONFIRM` asks for typed `CONFIRM` — anything else cancels honestly.
    4. **Countdown:** `handover_countdown_line()` → 10 seconds, ABORTABLE — "abort handover" / "cancel" → `LINE_HANDOVER_ABORTED`, zero wipe, flow dead. **Law 5 pins: the kill-switch during countdown = instant death, NO wipe fires.** Countdown completion alone triggers the wipe.
  - **Keys question at the gate (Part IX's "it asks"):** before the countdown, one honest question — keep or wipe the API keys — rides a YES/NO typed branch (both lawful, both pinned); in the sandbox the secrets mapping is caller-provided, so "wipe" asserts the *disowning* (the ring re-loads empty and refuses honestly), "keep" asserts keys stand. nt truth: the file erase is AiO-era — canon comment, fixture here.
  - **The wipe (per the §30 ledger):** vault personal tables emptied (memory, kv personal entries, sent_log, journal rows — schemas stand) · `profiles.json` wiped (voiceprints + passphrase) · `settings.json` RESET to factory (honesty 90, humor 5 — dial law stands) · `logs.jsonl`: personal entries purged, **exactly ONE line survives — `Handover executed <date>`** (shape pinned by date-pattern match) · `tars-brain/` wiped in full — the mind belongs to the commander who raised it; the farewell wipes the mind and keeps the machine (decree logged; line-230 law).
  - **KEPT — battery-pinned untouched:** the program/canon/laws · gauge/ring SCHEMAS (counters may reset — operational, not personal; declare the choice in code) · grammar/bible semantics (documents untouched trivially) · **Windows + user files: 100% OUTSIDE the blast radius — a negative-space battery pin asserts the wipe's root-set ⊆ {vault, profiles.json, settings.json, logs.jsonl personal lines, tars-brain/, (secrets mapping if disowned)} and NOTHING else is ever opened for write.**
  - **After:** first summon post-wipe → `LINE_FACTORY` EXACTLY *"Factory state. New commander, identify yourself. Honesty: ninety. Humor: five."* — mint LOCAL, speaks ONCE, then the standing enrollment flow owns the new commander. No second greeting, ever.
  - **Irreversibility law:** NO backup, NO undo seam, NO shadow copy — a wipe that secretly remembers is a lie with extra steps. Code-comment doctrine + grep-level battery pin (no path in handover.py may copy personal data anywhere).
- `command.py` — v1.6 rows: `"tars handover"` (the only opener) · `"abort handover"` / reuse standing cancel rows inside the flow · NO alias family (deliberate — this row must be hard to hit by accident; near-miss discipline stays sharp around it).
- `canon.py` — extend, generative + literal-pinned:
  - `LINE_HANDOVER_VOICE_ONLY = "Only Cooper hands TARS over."`
  - `LINE_HANDOVER_PASS = "Passphrase, please. Spoken."`
  - `LINE_HANDOVER_CONFIRM = "Type CONFIRM to erase my memories. This is a goodbye. It cannot be undone."`
  - `handover_countdown_line()` → `"Wiping in ten. Say abort to stop me."` (generative if the seconds move; number truthful, literal pinned)
  - `LINE_HANDOVER_ABORTED = "Handover aborted. Everything stays."`
  - `handover_keys_line()` → `"Keep the API keys for the machine? YES keeps them."` (pin)
  - `LINE_FACTORY = "Factory state. New commander, identify yourself. Honesty: ninety. Humor: five."`

## 2. The privacy + social regression net (the phase's second soul — §31)
- `selftest.py` gains the **audience-tier matrix battery:** enumerate EVERY personal surface — memory recall · persona memory block · people profiles · inner journal · brain rows (lessons/brain-summary/journal read-back) · sent-log recall · brain A3 explorer — × audience tiers {verified Cooper / family / guest} → **refusal/allow matrix pinned byte-exact**; PERSONAL-CANARY content swept ABSENT from every non-Cooper surface (and from every ring payload assembled under family/guest audience, the persona-omission law re-proven at matrix scale).
- edge-tts audience rule re-pinned (the P-CORE-3 ladder) under the new matrix: no personal text reaches the edge tier under any audience.

## 3. Ring discipline + crash laws
- The entire handover flow is LOCAL: zero ring spend at any gate, counter-pinned (a farewell never phones a friend).
- Crash child: SIGKILL DURING countdown → no wipe on reopen, countdown honestly dead, drill marker intact · SIGKILL MID-WIPE → reopen: either pre-wipe bytes or post-wipe state, never half-personal-left/half-gone per table (wipe order is transactional per store; the battery pins per-store atomicity).
- All 595 prior checks byte-stable except §7. Determinism ×2. Expect ≈650–675.

## 4. Grammar v1.6 (append-only; 3 example utterances per row)
Rows: handover open · abort. Row-for-row exercised; zero-ring counter-pinned.

## 5. Agent-log (one append-only entry)
What shipped · gate-orchestration shape · wipe root-set declaration · the kept-vs-wiped table as shipped · machine-taught fixes in the open · acceptance CORRECTION for P-CORE-10: "PASS, banked by Architect audit Aug-21 atop 24ada40 — 595/595 re-run twice, CANARY-INNER-31 sovereignty + call-cap-2 storm law + A3 confinement re-verified, roadmap acceptance pinned e2e."

## 6. Deliverable + REPORT block (§3.5 shape — mandatory)
Whole files · zero dead code · zero unused imports (seam patterns recognized) · zero >U+2100 glyphs in code AND docstrings · zero new deps · zero network.
Commit: `[CORE] P-CORE-11 — privacy net + Handover: audience-tier matrix over every personal surface, Part IX triple-gate + abortable countdown, keys question, sole-survivor log line, factory boot, grammar v1.6, <N>-check selftest`.
REPORT: FILES · 7-LAWS RECITAL · SELFTEST OUTPUT (fresh-clone tail, twice) · CONTRACT CHECK (channels closed, bus at 9) · KNOWN LIMITS (nt file-erase AiO-era, fixture here) · RE-AIMS · PUSHED (fresh-clone-verified green).

## 7. Sanctioned re-aims (the ONLY tolerated diffs; disclose in-code + REPORT)
1. Any prior pin that asserted personal rows answer WITHOUT an audience gate (if a row shipped Cooper-implicit before the matrix, it now hardens) — name each, re-prove the protected law on the gated vehicle.
2. Nothing else moves. Any further diff = FAIL.

**Never List + 7 Laws bind. Part IX's last sentence is the phase: irreversible — by design, this is a goodbye. The machine's truth over green lights. Leave cleanly.**
