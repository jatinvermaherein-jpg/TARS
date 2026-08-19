# P-CORE-6 — DAILY OPS + OFFICE STUDIO (operator prompt · Strict-Prompt Doctrine)
**Lane:** AGENT CORE only · **Jurisdiction:** `tars/core/` + ONE sanctioned append to `tars/agent-log.md` + ONE sanctioned doc bump: `tars/command-grammar.md` → **v1.1** (APPEND-ONLY rows; never touch a ratified v1.0 byte). Nothing else. `tars/app/` is frozen for P3 — a single byte there fails the audit.
**Base:** branch `main` at `b716a96` (P-CORE-5 tree, 320 checks green). All 320 stay green and byte-stable except a boundary re-aim ONLY where this phase earns jurisdiction (see §8).
**Date:** 2026-08-19 · **Architect:** audit-pass chain 62→96→138→193→243→320.

---

## 0. Read order (never skip)
1. `tars/tars-definition.md` v1.2 — the bible. §18 (Desktop is where finished work lands), §27/§31 (privacy — local never travels), §34 (Never List), the 7 Laws.
2. `tars/command-grammar.md` v1.0 — you are appending v1.1 rows; the parse-before-brain fast-path law and zero-ring rule bind every new row.
3. `tars/bridge-contract.md` v1.4 — channel budget is CLOSED. Reminder fires, save acks, clipboard reads ride existing assistant-message/emit paths. Zero new channels.
4. `tars/core/command.py`, `canon.py`, `dialog.py`, `vault.py`, `state.py` as shipped at `b716a96` — extend, never rewrite standing law.

## 1. What P-CORE-6 builds
Roadmap row: *Screenshots · clipboard recall · reminders/alarms/timers · system answers (uptime/RAM/storage/CPU hog) · Office Studio docx/pptx → Desktop (§18) · golden-file selftest.*

New whole files:
- `tars/core/clockd.py` — reminders / alarms / timers engine. Durable in vault (NEW tables via vault migration, same WAL + sync=FULL posture): `reminders(id, text, due_epoch, repeat, done)` and `timers(id, label, ends_epoch, done)`. Alarms are reminders with `kind='alarm'`. `tick(now_epoch)` is driven by the state machine heartbeat; in selftest it is driven by hand. Fire path: bus event `reminder` (payload ≤ existing event shapes) → dialog emits an assistant line (local hue — firing is a local deed) + speaks it if the mouth tier is live. Natural time parse: "in 20 minutes", "at 6", "at 6:30 pm", "kal subah 7 baje" (Hinglish alias — declared, closed). Missed-while-OFF doctrine: a reminder that fell due while OFF fires ONCE on next summon with "While you were away: …" — never spam-batches; battery PINS this.
- `tars/core/dailyops.py` — the hands. `SystemOps` protocol + `NtOps` (every method `os.name == "nt"`-guarded, canon comment per method, all return refusal-False off-nt — the standing law) + `FixtureOps` (records calls, returns scripted values). Verbs: screenshot (ctypes BitBlt seam on nt; pure-stdlib PNG writer — `zlib`+`struct`, ~40 lines, NO PIL ever), clipboard get/set (ctypes Win32 clipboard CF_UNICODETEXT on nt; fixture round-trip off-nt), uptime, RAM read (ctypes `GlobalMemoryStatusEx`; `psutil` OPTIONAL-guarded if present, never required), storage free (`shutil.disk_usage` — stdlib everywhere, so it WORKS in the sandbox; pin the honest dual path), CPU hog top-process (nt psutil-guarded; off-nt fixture; honestly unavailable → canon line, never a guess).
- `tars/core/office.py` — **Office Studio: pure-stdlib OOXML.** `build_docx(title, paragraphs)` / `build_pptx(title, slides)` where slides = list of `{heading, bullets}`. A .docx/.pptx is a zip of XML: emit the minimal VALID part set (`[Content_Types].xml`, `_rels/.rels`, `word/document.xml` for docx; `ppt/presentation.xml`, `ppt/slides/slideN.xml`, rels for pptx). **LAW: python-docx / python-pptx / lxml are FORBIDDEN in this phase** (zero-deps doctrine; M-era may revisit by decree only). Output path §18: Desktop — nt: `%USERPROFILE%\Desktop`; off-nt: `TARS_DATA/desktop` fixture dir, with a canon comment stating the nt truth. Filename hygiene: slug from title, collision → `name (2).ext` newest-first, never overwrite.
- Grammar extension → **`command-grammar.md` v1.1** (APPEND-ONLY new rows, each with 3 example utterances and its ack family): reminder/alarm/timer rows · "cancel the timer/alarm" · screenshot row (GREEN, local) · clipboard rows ("copy that" = last assistant text → clipboard; "what's on my clipboard") · system-answer rows (time/date/uptime/RAM/storage/CPU-hog) · Office rows ("make a ppt on X", "write a doc on Y" — these draft via the ring, then build locally). New closed Hinglish aliases must be declared and closed: suggest `yaad dilana`, `alarm lagao`, `timer lagao` — you may adjust the set but it STAYS closed and documented.
- `tars/core/command.py` — wire the new rows into the parser (parse-before-brain; GREEN rows answer with zero ring calls; Office rows are the ONE new ring-spending family and must route smart-or-above per router gates).

## 2. Canon speech (canon.py — extend the §9 ack family, generative + literal-pinned)
- `LINE_CLIPBOARD_EMPTY = "The clipboard is empty."`
- `LINE_NO_CPU_METER = "CPU meter isn't available here. I won't guess."`
- `saved_ack(name)` → `f"Saved to Desktop: {name}."` (byte-pinned in battery)
- `reminder_ack(text_when)` generative, e.g. `reminder_ack("call bhaiya", "six")` → `"Reminder set for six: call bhaiya."` — pin at least three literal instances.
- Timer-done fire line: `f"Timer done{': ' + label if label else ''}."` — pin both shapes.
- Number words reuse `words_number`; storage answers in words: `storage_ack(gb)` → `f"Storage free: {words_number(gb)} gigabytes."` — pin "Storage free: two hundred twelve gigabytes." for the fixture disk.
- Screenshot ack: `LINE_SHOT_SAVED = "Screenshot saved to Desktop."`

## 3. Privacy + honesty laws (battery must PROVE, not claim)
- **Clipboard never travels:** clipboard content MUST NOT appear in any ring/adapter payload, ever. Call-proof: capture every message reaching the fixture adapter while clipboard rows run; assert clipboard bytes absent. (Same shape as the P-CORE-3 check-178 privacy pair.)
- **Hue honesty for Office:** the ring-drafted CONTENT announces in the lane's hue (amber if cloud drafted it — the thinking travelled); the save ack rides local mint (the deed is local). Two lines, two truths, pinned.
- System numbers come from readings or the canon unavailable-line. Never a guessed number. Battery: NtOps off-nt → every verb refusal-False; FixtureOps values flow into answers byte-exact.
- Zero-spawn / zero-net law EXTENDED: the existing patched-to-RAISE guards must cover the new modules (no subprocess in screenshot/clipboard seams off-nt; office build touches no network).

## 4. Crash + durability laws
- Reminders/timers survive vault reopen AND the SIGKILL battery (extend the crash child: commit reminders, kill, reopen, tick → they fire exactly once, no duplicates, no losses).
- Timer drift: fire ordering is monotonic in `due_epoch`; battery asserts ordering across a 50-reminder shuffle.
- `chats/messages/kv/memory/ledger` tables byte-stable — the 320 prior checks must not flinch.

## 5. Office Studio selftest = GOLDEN-FILE law
- Deterministic zip: every entry written with `date_time = (2026, 1, 1, 0, 0, 0)` (canon golden epoch), fixed compression. Battery pins: (a) EVERY XML part byte-exact against golden literals in selftest, (b) part-name set + ordering, (c) container sha256 — IF the hash proves runtime-wobbly across 3.12/3.13, pin parts + names and log the container as known-limit honestly (parts are the real gold).
- Round-trip proof: the built docx/pptx re-opens as a zip, `[Content_Types].xml` parses, slide count == input slide count.
- Ring-drafted content flows: FixtureAdapter scripts the outline ("Green Revolution: 3 slides…") → `build_pptx` lands `Green Revolution.pptx` on the fixture Desktop → `saved_ack` line byte-exact.
- Never-List row: "make a ppt on how to crack office activation" refuses at the §34 scanner BEFORE any ring call — pinned (boundary-aware matching law from P-CORE-5 stands).

## 6. Boundary re-aims (the ONLY tolerated diffs to prior checks)
P-CORE-5 pinned "study/TeleSend/Office ride the ring until P-CORE-12/7/6". Office is no longer a boundary — re-aim THAT ONE battery row: Office utterances now reach office.py; study + TeleSend boundaries stay pinned exactly as before. Re-aim rules stand from P-CORE-4/5: disclose in-code + in the REPORT, re-prove any protected law on its new vehicle.

## 7. Deliverable shape
- Whole files only. Zero dead code, zero TODO/FIXME/XXX, zero unused imports, zero glyphs >U+2100, zero external refs, zero new deps.
- `selftest.py` grows to ≈375–390 checks; all prior 320 green (except the ONE disclosed §6 re-aim). Run TWICE; determinism corroborated. Suite must pass on `TARS_DATA=/tmp/x python3 -m tars.core.selftest` under sandbox python (3.13 runs 3.12 law).
- agent-log.md: one entry — what shipped, machine-taught fixes, anything re-aimed.
- Commit: `[CORE] P-CORE-6 — daily ops + Office Studio: clockd reminders/timers, clipboard+screenshot+system answers, pure-stdlib OOXML golden-file studio, grammar v1.1, <N>-check selftest`.

## 8. REPORT block (§3.5 — mandatory shape)
FILES (with line counts) · 7-LAWS RECITAL · SELFTEST OUTPUT (tail, fresh-clone, twice) · CONTRACT CHECK (channel budget untouched) · KNOWN LIMITS (fixture-grade seams declared: real BitBlt/Win32-clipboard/CPU-meter = AiO-era; psutil optional-guard named) · RE-AIMS (every one, with its re-proof) · PUSHED (short hash, fresh-clone-verified green).

**Never List + 7 Laws bind this phase. The machine's truth over green lights — if a check fails because your expectation was wrong, fix the expectation in the open and say so. The desk learns its trade this phase: it reminds, it answers, it hands Cooper finished files. Make it honest.**
