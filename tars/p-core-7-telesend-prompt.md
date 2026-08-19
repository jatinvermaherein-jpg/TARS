# P-CORE-7 — TELESEND (operator prompt · Strict-Prompt Doctrine)
**Lane:** AGENT CORE only · **Jurisdiction:** `tars/core/` + ONE sanctioned append to `tars/agent-log.md` + ONE sanctioned doc bump: `tars/command-grammar.md` → **v1.2** (APPEND-ONLY; never touch a v1.0/v1.1 byte — P-CORE-6's zero-removed-lines proof is the standing pattern). `tars/app/` frozen. Nothing else.
**Base:** branch `main` — P-CORE-6 tree, **385 checks green** (audit PASSED, banked Aug 19). All 385 stay green and byte-stable except the §7-sanctioned boundary re-aims.
**Date:** 2026-08-19 · suite chain 62→96→138→193→243→320→385.

---

## 0. Read order (never skip)
1. `tars/tars-definition.md` v1.2 — **§17 (stage→show→YES: nothing outbound without Cooper seeing the exact bytes)**, §27/§31 privacy, §34 Never List, the 7 Laws.
2. `tars/roadmap.md` P-CORE-7 row — USER lane Telethon (login-once session) · BOT lane elective · WhatsApp **wa.me text lane, file-send OFF** · stage→show→YES · acceptance: *selftest against Telethon in dry-run/mock; gate flow verbatim*.
3. `tars/bridge-contract.md` v1.4 — channel budget CLOSED; staging rides the EXISTING `action` event machinery (kind `"telesend"`, flat scalars) + the typed-YES gate from command.py. Bus stays at 9 types. Zero new channels.
4. Standing tree: `command.py` (typed-YES gate, Never-List pre-scan, near-miss discipline), `findfile.py` (confident-single / honest-list), `keys.py` (caller-provided secrets posture), `vault.py` (WAL+FULL migrations), `canon.py` (generative + literal-pin ack law).

## 1. What P-CORE-7 builds
**TARS's words leave the box for the first time. The gate is the phase.**

- `tars/core/telesend.py` — NEW. The outbound engine:
  - `TeleClient` protocol: `send_text(recipient, text)`, `send_document(recipient, path)`, `linked()` status.
  - `TelethonUserClient` — the REAL codepath, **import-guarded optional** (Telethon is NOT a sandbox dep and never becomes one; the psutil/whisper posture exactly): `os.name == "nt"` AiO-era seam, session file under `TARS_DATA`, `api_id`/`api_hash` arrive ONLY via caller-provided secrets mapping (the keys.py law — never auto-read env, never in repo, never logged). Absent lib/session/credentials → honest unavailable, ZERO wire attempts, canon refusal. Every nt call carries the canon comment.
  - `FixtureTelethon` — the dry-run/mock twin: records every (`method`, args) call, scripted success/failure, `linked` scripted. **This is the suite's Telethon** (roadmap acceptance: dry-run/mock).
  - **BOT lane: DEFERRED BY DECREE.** Roadmap marks it elective; zero-dead-code beats a stub. Build NO bot surface this phase — declare the deferral in KNOWN LIMITS.
  - `wa.me` text lane: builds the exact URL `https://wa.me/<digits>?text=<urlencoded>` from the people-book number; delivery = the operator open-url seam (fixture-recorded in sandbox — no browser spawns here). **File-send on WhatsApp stays OFF**: the row answers the canon line, no staging. Decree: `LINE_WA_FILES_OFF = "WhatsApp file-send stays off. Telegram carries files."`
- People-book — vault migration (same WAL+FULL posture): `contacts(id, name, telegram, whatsapp, added_on)`; name = lowercase key, display kept. Rows: "save bhaiya's telegram as @arjun_verma", "save ma's whatsapp as +91…", "forget bhaiya", "who do I know" → honest numbered list newest-first. Unknown recipient → ONE clarifying question (near-miss discipline), never a fuzzy guess — the I-don't-guess doctrine. Duplicate name → honest line, never silent overwrite.
- Gate flow (§17, single-use actionId, 120s expiry, cancel-consumes — REUSE the standing typed-YES machinery, do not fork it):
  1. **stage**: build the exact outbound payload (verbatim text by default — ZERO ring spend; see §3 for the one lawful ring draft).
  2. **show**: one staged-preview line carrying the exact bytes + channel + recipient — battery pins the format; must contain, in order: recipient display name, channel name, the quoted payload, `type YES`. Action event `kind:"telesend"` (flat scalars only).
  3. **YES**: executes EXACTLY once → fixture/real send → delivery ack (generative + pinned): `sent_ack("bhaiya", "Telegram")` → `"Sent to bhaiya on Telegram."` · wa lane: `opened_ack("ma")` → `"Opened WhatsApp for ma. Review and press send there."` (honest: TARS opens the door, the human's thumb sends).
  4. cancel / expired / unknown id → `LINE_CANCEL` round-trip, zero sends, byte-identical to the P-CORE-5 gate law.
- File send (Telegram only): FileFinder confident-single → stage with FULL PATH shown → YES → `send_document`. Multi-match → honest capped list, never a guess. Never-List scan BEFORE staging (§34 at every row). File bytes NEVER enter a ring payload.
- Sent ledger — vault `sent_log(id, channel, recipient, kind, summary, sent_epoch)`, append-only. Only SUCCESSFUL sends journaled; failures answer the canon failure line and journal NOTHING (the ledger records what left the box — honesty, not intent). Recall row: "what did I send bhaiya" → honest list newest-first, capped per finder-law.

## 2. Canon speech (extend, generative + literal-pinned)
- `LINE_TELE_NOT_LINKED = "Telegram isn't linked yet. Setup happens on the AiO."`
- `LINE_TELE_FAILED = "That send didn't go through. Nothing left the box."`
- `LINE_WA_FILES_OFF` (decreed above) · `no_contact_line(name)` → `f"I don't know {name} yet. Save them first."`
- `sent_ack` / `opened_ack` (§1) · staged-preview line (§1 — its bytes become §17's face; pin at least three literal stagings: tele-text, tele-file with path, wa-text).
- Staged DRAFT via ring (only when asked, see §3): the draft line rides the lane hue (two-truths pair, Office pattern), the staged preview stays local-the-gate hue.

## 3. Ring discipline + privacy laws (battery PROVES, never claims)
- **Verbatim compose = ZERO ring spend** — counter-pinned across the whole battery.
- The ONE lawful ring spend: Cooper asks TARS to *draft* ("send a birthday wish to ma") → smart lane drafts → draft rides the lane hue → stage shows the DRAFTED bytes exactly. One spend per draft, pinned.
- **Pre-YES zero-wire LAW:** no TeleClient/wa-open call before YES — call-proof battery with a canary payload (SEND-CANARY pattern, the CLIP-CANARY-17 shape): canary absent from all adapter/ring payloads pre-YES; present in exactly one `send_text` post-YES.
- Never-List pre-stage at every send row; refusal = LINE_NEVER_LIST, zero gate, zero wire, logged (extend the standing battery — same shape).
- Clipboard/file bytes never in ring payloads (standing law — re-pin on send rows).

## 4. Grammar v1.2 (append-only doc bump, 3 example utterances per row)
- Rows: tele-text send · tele-file send · wa-text send · contact save/forget/list · sent-log recall · cancel rides the standing row. Closed Hinglish aliases declared (suggest `bhejo`; adjust but CLOSED). Every row exercised end-to-end in the battery — the v1.0/v1.1 row-for-row law stands.

## 5. Guards, crash, determinism
- urlopen / subprocess.run / Popen patched-to-RAISE must cover the new battery (fixture transport is a python object; the sandbox never dials).
- Crash child gains a clock+send-journal workload: SIGKILL → reopen → journal rows intact, no duplicate sends on tick replay, integrity ok.
- All 385 prior checks byte-stable except §7. Determinism ×2 minimum here; expect ≈445–465 total.

## 6. Agent-log (one append-only entry)
What shipped · key facts for future phases (gate reuse shape, people-book schema, two-truths draft pair, wa lane mechanics) · machine-taught fixes in the open · **acceptance CORRECTION for P-CORE-6**: "PASS, banked by Architect audit Aug-19 atop 8637cf5 — 385/385 re-run twice, grammar v1.0 zero-removed-lines proven, five prompt-consequent re-aims accepted, CLIP-CANARY privacy law re-verified."

## 7. Sanctioned re-aims (the ONLY tolerated diffs; disclose in-code + REPORT, re-prove the protected law)
1. Boundary battery: tele-text / tele-file / wa-text utterances LEAVE the boundary (they're real rows now). **Stays pinned as boundary:** study · **whatsapp FILE send** (LINE_WA_FILES_OFF is a row, not a boundary) — assert exactly one matching boundary change set.
2. Any pending-pin from earlier phases that THIS phase's earned jurisdiction retires — name each.

## 8. Deliverable + REPORT block (§3.5 shape — mandatory)
Whole files only · zero dead code · zero unused imports (**documented re-exports are live surface — if you keep one, keep its comment; the audit scanner now knows the pattern**) · zero >U+2100 glyphs · zero new deps · zero network.
Commit: `[CORE] P-CORE-7 — TeleSend: stage→show→YES outbound gate, Telethon user-lane seam (dry-run/mock battery) + wa.me text lane, people-book, sent ledger, grammar v1.2, <N>-check selftest`.
REPORT: FILES (line counts) · 7-LAWS RECITAL · SELFTEST OUTPUT (fresh-clone tail, twice) · CONTRACT CHECK (channels closed, bus at 9, action kind "telesend") · KNOWN LIMITS (bot lane deferred-by-decree; Telethon real-twin unproven until the AiO; wa lane = open-url seam) · RE-AIMS · PUSHED (short hash, fresh-clone-verified green).

**Never List + 7 Laws bind. §17 is the soul of this phase: Cooper sees the exact bytes, then — and only then — the box speaks to the world. The machine's truth over green lights. Make every send earn its YES.**
