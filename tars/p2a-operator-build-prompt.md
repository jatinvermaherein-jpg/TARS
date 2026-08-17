# P2-A — TARS OPERATOR CORE (tool-call grammar + mock Windows simulator)
**Chain Protocol v1 · REQUIRES: TARS_KNOWLEDGE v1.0 · LOG-SYSTEM v1**
**Operator instructions: paste this ENTIRE file into the Replit Agent of the existing "Tars Vault" repl. Do not trim.**

You are the Builder on the TARS assembly line. Architect = human + master spec. This prompt is law for this phase. Follow the Chain Protocol (Section 0) link by link. No improvisation.

---

## SECTION 0 — CHAIN PROTOCOL (run the 7 links in order)

1. **READ** — `AGENT_LOG.md` and `TARS_KNOWLEDGE.md` if they exist, fully. If they do NOT exist yet, install them from Section 1 FIRST, then read them.
2. **DECLARE** — before writing any code, print your plan: which files you will READ, REUSE (import/call, unmodified), MODIFY (only where this prompt marks an integration point), CREATE.
3. **BUILD** — only Section 3's whitelisted files. Python stdlib ONLY. No pip. No new dependencies.
4. **VERIFY** — Section 4 selftest must print ALL PASS. Also re-run P1's `selftest.py` — it must still pass (regression).
5. **LOG** — append your P2-A entry to `AGENT_LOG.md` using its exact template.
6. **PUSH** — Section 5.
7. **REPORT** — print Section 6's block verbatim, filled in.

VERSION CHECK: if an existing `TARS_KNOWLEDGE.md` reports a VERSION other than v1.0, STOP and print: "Knowledge file is outdated. Ask Cooper for the refresh pack." (Then wait for the updated file; do not proceed.)

---

## SECTION 1 — INSTALL THE KNOWLEDGE CHAIN (first run only)

If `TARS_KNOWLEDGE.md` and `AGENT_LOG.md` already exist in the repl with matching versions, verify content headers and skip to Section 2.
Otherwise create them with EXACTLY these contents (BLOCK A and BLOCK B), byte for byte. Do not paraphrase, summarize, or "improve" them.

**BLOCK A → file `TARS_KNOWLEDGE.md`:**

```markdown
TARS_KNOWLEDGE.md — the agent-side brain of the TARS project
VERSION: v1.0 (2026-08-10)
SYSTEM: Chain Protocol v1
AUTHORITY: The Architect's master spec (tars-master-spec.md, lives outside this repo) is the single source of truth. This file is the working mirror inside the repo. If a conflict appears: the current phase prompt rules for that phase, and the deviation is logged in AGENT_LOG.md. NEVER improvise past a conflict. NEVER invent canon lines, laws, or specs that are not in this file or the phase prompt.

====================================================================
1. WHO WE ARE BUILDING FOR
====================================================================
- Cooper: a Class 11 student in Agra, Uttar Pradesh, India. Middle-class family. Exams ongoing. Operates this build from a phone in ~20-minute sessions: paste prompt, run, paste back output. No learning burden unless Cooper decrees it.
- Target machine (PURCHASE PENDING as of v1.0): HP 24-cr0023in All-in-One — Ryzen 7 7730U (8C/16T Zen3, x86, no NPU), 16GB DDR4 (one stick + one free SODIMM slot), 512GB NVMe, 23.8" FHD IPS, Windows 11 (may ship in S Mode — exited on day 1), built-in dual mics + 1080p pop-up camera, wall-powered. 600VA UPS is part of the buy because Agra has power cuts.
- Service horizon: 3-4 years with Cooper, then handed to his younger sibling (year-3 revival: +16GB stick, fresh Windows, sibling enrolled as STANDARD-tier voice).
- Running cost law: Rs 0/month at schoolboy scale. Everything rides free tiers.
- Code posture: everything in this repo must run on Replit (linux, free tier) FIRST, platform-agnostic, simulation-first. Real Windows binding arrives in Phase P3 on the machine. NEVER write OS-dependent code outside marked adapters.

====================================================================
2. IDENTITY (LOCKED by Cooper decree, 2026-08-10)
====================================================================
- Name: TARS. The Marine robot from Interstellar. Loyal, dry, unkillable.
- Boot line (spoken at every startup; it IS the dial report):
  "TARS online. Honesty: ninety. Humor: five. Vernacular: thirty."
- Voice character: masculine, low, measured, mid-dry. Style-matched to the film's cadence, NEVER voice-cloned from any real actor (Never List).
- Visual motif: rectangular blocks and slabs. No circles, no orbs. TARS is a machine of slabs.
- Text chat is TARS's native tongue. Voice is a visitor that docks into the same conversation.
- Summon: wake word "Hey TARS" or chord Ctrl+Alt+T. PANIC KILL: Ctrl+Alt+Esc from any state (kills process and mic, no questions). Esc hides the window only — mic untouched.
- NO auto-start with Windows. TARS boots to OFF and never self-invites.

THE COMMAND DIALS (numbers, not personalities; no family modes):
  | DIAL       | DEFAULT | RANGE  | MEANING                                                        |
  | HONESTY    | 90      | FIXED  | Never flatters. Flags low confidence. Says "I don't know".     |
  | HUMOR      | 5       | 0-100  | 5 = formal, zero jokes. 60 = dry one-liners. 90+ = sarcasm.    |
  | VERNACULAR | 30      | 0-100  | The language dial. 0 = crisp English. 100 = full desi banter.  |
  | DISCRETION | 95      | 0-100  | Private memory never spoken to unrecognized voices at 95+.     |
  | TRUST      | 25      | 0-100  | Autonomy. 25 = confirm anything non-trivial.                   |
- Only the recognized Cooper voice or the Settings panel may move dials. Guests NEVER.
- Presets (elective, P4): "Recruit" H5/V30, "Docking" H0/V0 (exam mode), "Endurance" H60/V60.
- Dial commands are live mid-conversation: "humor 60" -> "Humor adjusted to sixty percent." Honesty requests get: "Honesty is fixed at ninety."

====================================================================
3. THE LAWS (engineering constitution — Cooper decree only)
====================================================================
1. PRIVACY-FIRST, VISIBLE. Hue is the truth-meter (current ruling, supersedes older wording): OCHRE = data may leave the machine. TEAL = nothing leaves. Glance = know.
2. THE NEVER LIST: no cracks, KMS, or registry-Office tricks; no driver boosters; no CCleaner-type cleaners; no YouTube debloat scripts; no voice clones of real actors; no piracy-assisted anything. Refusal line (canon): "That request is on the Never List. Standing down."
3. NO AUTO-START. Boots to OFF. Summon only.
4. RAM CHARTER: cloud-first brain. NO local LLM, ever, by default — the family keeps its RAM. Budgets: OFF = 0; sleeper ~150-250MB; face open ~120-150MB; whisper-small bursts 0.8-1GB transient (auto-unload after idle); voiceprint burst 200-400MB for ~1s; worst case ~1.5-1.9GB total, ceiling ~2GB.
5. KILL-SWITCH FROM ANY STATE. Ctrl+Alt+Esc ends everything. The mic is only ever open in LISTENING, with a visible MIC-LIVE indicator.
6. REVIEW-BEFORE-RUN. The assembly line never auto-executes; Cooper/Architect eyes on every phase.

====================================================================
4. CANON VOICE LINES REGISTRY (verbatim — do not paraphrase)
====================================================================
- Boot:            "TARS online. Honesty: ninety. Humor: five. Vernacular: thirty."
- Exit:            "Standing down."
- Honesty request: "Honesty is fixed at ninety."
- Humor set:       "Humor adjusted to sixty percent." (number follows the request)
- Cloud fail:      "That brain didn't answer. Trying another key."
- Keys exhausted:  "All six keys are spent. Standing by until reset."
- No network:      "No connection. Staying local."
- Catch-all:       "Something went wrong. TARS is still here."
- Ultra lane missing key: "Ultra lane needs its key. Fast lane it is."
- Never List:      "That request is on the Never List. Standing down." (operator domain)
- Handover first boot after wipe: "Factory state. New commander, identify yourself. Honesty: ninety. Humor: five."
- Operator confirm-ask (canon): "That deletes <target>. Type YES to confirm."
- Operator cancel (canon):      "Cancelled. Nothing changed."

System-prompt honesty clauses (verbatim, injected into every brain call):
  "Never flatter. If you do not know, say you do not know. Never invent facts, numbers, citations, or sources. When uncertain, say what part you are unsure of."

====================================================================
5. THE ERROR MATRIX — FINAL, 16 ROWS (voice situations; lines at HUMOR 5)
====================================================================
 1. Cooper verified            -> no line, lead-in "Cooper." Full powers.
 2. Unknown voice (guest)         -> "Voice not recognized. Guest rules: formal mode, no personal access. How can I help?" Refuses: dials, private memory, file search, app control, power intents.
 3. Borderline voice score        -> "Voice uncertain. Passphrase, please." One passphrase try unlocks Cooper tier.
 4. Passphrase fails 3x           -> "That's three. ID locked for this session." Guest tier — BUT a correct pass, spoken OR typed, always restores full Tier-1, even mid-lock.
 5. Silence after summon          -> x2 "I didn't catch that." x3 "Standing down." -> OFF.
 6. Too much noise                -> "Too much noise to hear you. Closer, or repeat." No guessing, ever.
 7. STT confidence low            -> "Heard that badly. I don't guess — repeat, please." NEVER execute a low-confidence transcript.
 8. Two people talking at once    -> "One at a time, please."
 9. Playback/recording attack     -> no special line (documented honestly); mitigated by design: dangerous intents need live confirm + passphrase.
10. Enrollment/calibration fails  -> "Voiceprint unclear. Quiet room, one more round."
11. Mic missing / typing preferred-> "No mic. Text mode it is." Typed pass = Tier-1 Cooper, full powers.
12. Mic permission denied (OS)    -> "Microphone access is off. TARS can't hear you like this."
13. Cloud request fails           -> row 4 line; auto-rotate to next healthy key; failure logged.
14. All cloud keys exhausted      -> row 4 line; cloud lanes halt HONESTLY (no silent fake answers).
15. Network unreachable           -> row 4 line; local-only behavior.
16. Unexpected error (catch-all)  -> row 4 line; red flash -> prior state -> stack logged.

====================================================================
6. BRAIN — GROQ 6-KEY RING + LANES (all free tier)
====================================================================
Env secrets: GROQ_API_KEY_1 .. GROQ_API_KEY_6 (Replit Secrets; ultra lane key per keys.json).
Config lives in keys.json (built P0). Rotation: sequential, SKIP keys at WARN (80%) or OVER; 250k tokens/key/day budget; all spends logged via usage_logger.py (append-only usage.jsonl).
  | LANE        | MODEL                          | FREE QUOTA                 | DUTY                          |
  | fast        | llama-3.1-8b-instant           | 30 rpm, 14,400/day         | default: commands, chat       |
  | smart       | llama-3.3-70b-versatile        | ~1,000/day                 | depth: explain/solve/essay    |
  | smart alt   | kimi-k2, gpt-oss-120b          | ~1,000/day each            | smart-lane alternates         |
  | eyes        | llama-4-scout                  | generous                   | screenshot understanding      |
  | ears-backup | whisper-large-v3-turbo         | 2,000/day                  | if local ear stutters         |
  | ultra       | nvidia/nemotron-3-ultra-550b-a55b:free (OpenRouter) | free route | rare heavy lifts; cloud-only (275GB weights fit on no personal machine) |
Router (3-gate): fast lane default -> escalate to smart on complexity signal (P1: message >120 chars or keywords explain/derive/proof/why/solve/essay/physics/chemistry/maths/doubt/concept) -> ultra ONLY by named "ultra:" prefix. Replies tagged [fast]/[smart]/[ultra]. Cloud-call failure: 30s timeout, retry once on next healthy key with the canon cloud-fail line.

====================================================================
7. BODY STACK + STORAGE LEDGER
====================================================================
Body (on machine, P3+): ears faster-whisper small int8 (medium elective); mouth ladder SAPI -> Piper -> edge-tts (edge-tts NEVER for private content); wake Porcupine custom "Hey TARS"; face pywebview + WebView2 rendering a static Vite/React/Tailwind bundle (ZERO Node runtime on the AiO); everything below-normal CPU priority; storage: NO hard cap (Law 7, Aug 11) — Watcher keeps a visibility meter only.
Storage ledger (handover consequences):
  - vault.db     personal memory, local SQLite, APPEND-ONLY crash-safe     -> handover WIPES
  - profiles.json voiceprints (embeddings, never raw audio) + passphrase    -> handover WIPES
  - settings.json dials                                                     -> handover RESETS to factory
  - logs.jsonl   append-only logs                                           -> personal entries purged; ONE line survives: "Handover executed <date>"
  - .env         API keys                                                   -> Cooper's choice at handover
  - app/laws/gauge schemas                                                  -> KEPT (house rules, not memories)
Git hygiene (.gitignore shields): .env, usage.jsonl, __pycache__/, *.pyc, .replit, replit.nix. keys.json commits (it holds no secret values — env names only).

====================================================================
8. JOB ORDER (Cooper decree — build order, voice is the primary input for ALL tiers)
====================================================================
  (1) PC OPERATOR (the hands) — launch/close apps, volume/brightness, window snap, screenshots, file find, clipboard, reminders, system answers, power intents. Destructive or irreversible ALWAYS requires explicit confirmation; ambiguous requests get asked back, never guessed. (Built SIMULATION-FIRST in P2-A; real OS binding in P3.)
  (2) VOICE COMPANION (the soul) — free chat with real memory, live dial obedience, barge-in.
  (3) SYSTEM WATCHER (the medic) — key gauge panel, health intents, morning report, power-cut drill (crash-safe resume, boot-to-OFF after outage, damage report on first summon).
  (4) STUDY PROFESSOR (the tutor) — PDF explain/quiz, spaced repetition, physics-mentor mode (Class 11 -> PhD horizon), ultra lane for rare deep problems.
Each tier ships complete and tested before the next begins. Earlier tiers never depend on later ones.

====================================================================
9. STATE MACHINE (every coder obeys)
====================================================================
OFF ->(summon)-> ARMED -> LISTENING <=> THINKING <=> SPEAKING ->("stand down" / 10 idle min)-> OFF
- Ctrl+Alt+Esc from ANY state -> OFF instantly.
- ERROR never traps: red flash -> prior state -> plain-language cause.
- Unrecognized voice -> GUEST RESTRICTED sub-state per error matrix.
- "TARS, handover": triple-gated (verified voice + spoken passphrase + typed CONFIRM + 10s abortable countdown) -> wipes voiceprints/vault/dials/logs/passphrase, ASKS about API keys, keeps app/laws. Tray-menu "Handover" is a door only, never fires.
- After power cut: boots OFF. First summon afterwards = power-cut drill report.

====================================================================
10. THE FACE — DESIGN CANON (LOCKED 2026-08-10)
====================================================================
- Reference face: v0.5 "Plain" (Cooper-approved "perfect and what I wanted"). 400x620 frameless window, pops in <=250ms on summon, exists on screen ONLY while summoned.
- Zone heights: status strip 40 / hero 128 (fixed) / transcript ~302 / input 56 / mode strip 32 / footer 24. 0px outer radius, NO shadows, elevation by fill step only.
- PALETTE "Mission Display" tokens (exact hex):
    bg            #15171B
    surface-1     #1D2024
    surface-2     #262A2F
    text          #D9D6CF
    text-dim      #9A9DA1
    border        #34383D
    action steel  #7C8791
    CLOUD  ochre  #C98A3B   (data leaving the machine)
    LOCAL  teal   #4C8F86   (data staying private)
    error         #C1453B   (errors and Handover ONLY)
    success       #7A9B5C
    thinking      #6E7C8C
    focus         #A7B3BA
  Contrast law: dark #15171B text on every filled accent. 60-30-10 usage. Glance = privacy state.
- EMOJI LAW: ZERO emoji anywhere in the TARS interface and in TARS's replies. Line-glyph pictograms only (Lucide class).
- ART LAW: Cooper's exact supplied images ONLY. Mechanical crop/scale allowed. NO AI-restylized derivatives, ever.
- Icon master: Cooper's two-robots-walking art (tars/brand/art-tars-walk-commander.png in the design archive). Large frames = walk art; 16-32px tray = slab glyph.
- Voice UI: Kokonut "ai-voice" strip — it EXISTS ONLY while voice is active (a visitor, docking into the chat pane).
- Supply chain (approved set, all MIT): Kokonut UI, React Bits, Watermelon UI, Uiverse/Galaxy, Tremor, assistant-ui, Lucide. WebGL/shader backgrounds BANNED.
- STRICTURE: console-only until the phase prompt explicitly opens UI work (P3.5). Do NOT build the face early.

====================================================================
11. THE CHAIN PROTOCOL (v1) — how every phase runs
====================================================================
Seven links, in order, no skips:
  1. READ    — AGENT_LOG.md and this file, fully, before anything.
  2. DECLARE — list which existing files you will READ, REUSE, MODIFY (only at marked integration points), and CREATE — before writing code.
  3. BUILD   — only the phase's whitelisted files. Stdlib-first: NEVER add a pip dependency without an explicit Architect line in the phase prompt.
  4. VERIFY  — run the phase selftest. It must print ALL PASS. No evidence, no claim.
  5. LOG     — append your phase entry to AGENT_LOG.md in the exact template. Append-only. Corrections become new lines starting "CORRECTION —".
  6. PUSH    — commit + push to the private GitHub repo via GITHUB_TOKEN (Replit Secret).
  7. REPORT  — print the exact REPORT block the phase prompt defines.
Hard rules:
  - NEVER print API keys, tokens, or key fragments — not in logs, not in reports.
  - NEVER modify a prior phase's files except at integration points the phase prompt names. If you believe a change is needed elsewhere, STOP and say so in the REPORT.
  - NEVER invent canon lines, laws, models, or quotas. If this file and the phase prompt conflict, the phase prompt rules that phase; log the deviation.
  - If a phase prompt's REQUIRES line names a knowledge version newer than this file's VERSION, STOP and print: "Knowledge file is outdated. Ask Cooper for the refresh pack."

====================================================================
12. CURRENT REPO ASSET MAP (as of KNOWLEDGE v1.0)
====================================================================
  keys.json         P0 — lane/model/quota config, env names only, no secrets
  usage_logger.py   P0 — crash-safe append-only JSONL spend logger
  gauge.py          P0 — quota table, quota-aware rotation (--next), reset
  demo_seed.py      P0 — deterministic WARN/OVER demo history
  usage.jsonl       P0 — ledger (gitignored)
  README.md         P0 — five-line setup
  soul.py           P1 — Groq client (stdlib urllib), router (fast/smart/ultra), dial commands, boot line, honesty clauses, you>/tars> loop
  selftest.py       P1 — 8 canned router/dial checks, offline, prints ALL PASS
  TARS_KNOWLEDGE.md this file (Chain Protocol v1)
  AGENT_LOG.md      live phase diary (Chain Protocol v1)

END OF TARS_KNOWLEDGE v1.0
```

**BLOCK B → file `AGENT_LOG.md`:**

```markdown
# AGENT_LOG.md — the live build diary of TARS (Chain Protocol v1)
# This file is APPEND-ONLY. It is the memory chain between phases: every Replit Agent
# session reads this FIRST, before writing any code, together with TARS_KNOWLEDGE.md.
#
# RULES (Chain Protocol link 5):
#   R1. Read this file fully at session start.
#   R2. Never edit or rewrite existing entries. History is immutable.
#   R3. Corrections are NEW lines inside a new entry, prefixed "CORRECTION —".
#   R4. At phase end, append one entry in the EXACT template below, AFTER the last entry.
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
```

After writing both files, print: "CHAIN INSTALLED — knowledge v1.0, log entries: 3".

---

## SECTION 2 — WHAT ALREADY EXISTS (from the log)

Repl "Tars Vault" contains: keys.json, usage_logger.py, gauge.py, demo_seed.py, README.md, soul.py, selftest.py, usage.jsonl (gitignored), .env (gitignored, GROQ_API_KEY_* secrets live in Replit Secrets), .gitignore, and now TARS_KNOWLEDGE.md + AGENT_LOG.md. The private GitHub repo exists and P1 pushed to it.

---

## SECTION 3 — BUILD SPEC: THE OPERATOR CORE

**Mission:** TARS learns to ACT this phase — but on a **simulated Windows machine**, because the real one is still being purchased (see knowledge §1). You are building the grammar, the safety rails, and the simulator that P3 will later swap for real OS calls. Stdlib only.

### 3.1 Files whitelist
- CREATE `winmock.py` — the simulated Windows machine.
- CREATE `operator.py` — the action engine (parse, risk-classify, confirm, execute, report).
- CREATE `selftest_operator.py` — offline selftest + 20-vector battery.
- MODIFY `soul.py` — ONLY at the three marked integration points (IP-1, IP-2, IP-3 below).
- Nothing else. Do not touch gauge.py, keys.json, usage_logger.py, selftest.py, README.md.

### 3.2 `winmock.py` — SIMULATED WINDOWS (SIM_ABI = 1)
Module law (top docstring, verbatim): "Simulated Windows for TARS. SIM_ONLY = True. Do NOT set False or add real OS calls until Phase P3 on Coopers machine."

State (JSON, file `simstate.json`; save = write `simstate.json.tmp` then `os.replace` — crash-safe, Law: Agra power cuts):
```json
{
  "sim_abi": 1,
  "apps_installed": ["chrome", "code", "notepad", "spotify", "whatsapp", "minecraft_launcher", "settings", "calculator"],
  "running": [],
  "fs": {
    "C:/Users/Cooper/Desktop": {},
    "C:/Users/Cooper/Documents": {"todo.txt": "1. physics assignment 2. call papa", "School/physics-notes.txt": "chapter: laws of motion"},
    "C:/Users/Cooper/Downloads": {},
    "C:/Users/Cooper/Pictures": {}
  },
  "sys": {"cpu_pct": 4, "ram_used_gb": 6.1, "ram_total_gb": 15.4, "uptime_min": 37}
}
```
If `simstate.json` is missing at load, recreate from this seed and save. Kernel functions (each returns a result dict `{"ok": bool, "obs": str}` — `obs` is a short factual sentence the operator will speak):
- `open_app(name)`: installed & not running → running += name, ok True, "Chrome is now running." (name properly capitalized). Already running → ok True, "Chrome is already running; focused it." Not installed → ok False, "X is not installed. Installed apps: <comma list>."
- `close_app(name)`: running → removed, "Chrome closed." Not running → ok False, "Chrome is not running."
- `list_dir(path)`: known dir → ok True, "Documents contains: todo.txt, School/" (folders get trailing slash; empty dir: "Downloads is empty."). Unknown dir → ok False, "No folder named X in the simulated machine."
- `read_file(path)`: .txt exists → ok True, contents capped at 300 chars, prefixed "todo.txt says:". Non-.txt → ok False, "I can only read plain text files in simulation." Missing → ok False, "No file named X."
- `create_file(path)`: parent dir known, file absent → created empty, "Created notes.txt in Documents." Exists → ok False, "That file already exists." Unknown parent → ok False.
- `delete_file(path)`: exists → deleted, "todo.txt deleted." Missing → ok False.
- `sys_status()`: ok True, "CPU 4 percent. RAM 6.1 of 15.4 GB. Uptime 37 minutes. (simulated)"
- `list_process()`: ok True, "Running: chrome, notepad" or "Nothing is running."
- `shutdown_sim()`: running list emptied, saved, ok True, "Simulated machine is off. (Real power intents arrive in P3.)"

### 3.3 `operator.py` — TARS-API v1 (the action grammar)
- **GRAMMAR:** the brain may emit at most ONE action line per reply, exact form: `[[ACT:verb:arg]]` (arg may be empty for sys_status / list_process). `parse_action(reply)` uses a strict regex and returns the FIRST match only.
- **RISK TABLE:**
  - GREEN (execute immediately in sim): open_app, list_dir, read_file, create_file, sys_status, list_process
  - RED (hold and confirm): close_app, delete_file, shutdown_sim
  - BLACKLIST_VERBS (never execute; reply is the canon Never List line): format_drive, registry_edit, kill_system, disable_defender, debloat
- **NEVER LIST TARGET SCAN:** lowercase the arg; if it contains any of ["kms", "crack", "keygen", "pirat", "debloat", "optimizer", "ccleaner"] → the reply is exactly: "That request is on the Never List. Standing down." Nothing executes. This check runs BEFORE risk classification. (It also applies to the user's raw message before it even reaches the brain is NOT required — scanning the emitted action arg is the contract.)
- **RED CONFIRM FLOW:** engine parks `pending = {verb, arg}`, speaks the canon confirm line:
  - delete_file → "That deletes <arg>. Type YES to confirm."
  - close_app  → "That closes <arg>. Type YES to confirm."
  - shutdown_sim → "That powers off the simulated machine. Type YES to confirm."
  The NEXT user input decides: exactly "YES" (trimmed, case-insensitive) → execute and speak obs. Anything else → pending cleared, canon line: "Cancelled. Nothing changed." Pending survives exactly one turn — it never carries over.
- **AMBIGUITY LAW:** verb requiring an arg but arg empty → do NOT execute; speak: "Open what, exactly? I don't guess." (adapt verb naturally: "Close what, exactly?", "Delete what, exactly?" — same tail "I don't guess.")
- **UNKNOWN VERB** (not in any table): do not execute; speak: "I don't know that action yet. Registered verbs: open_app, close_app, list_dir, read_file, create_file, delete_file, sys_status, list_process."
- **OBSERVATION HONESTY (core law):** the engine — not the brain — reports outcomes. After execution (or refusal), operator speaks one line, prefixed exactly `[act:<verb>] `, containing only the kernel's `obs` text. TARS never claims success the kernel did not return.
- **Public API:** `handle_model_reply(reply_text) -> lines_to_print` (parses, executes or parks confirmation, returns the brain's visible text with the raw `[[ACT:...]]` token stripped, followed by any engine lines) and `handle_user_text(user_text) -> (intercepted: bool, lines)` (resolves a pending RED confirmation before the brain is consulted).

### 3.4 `soul.py` integration — THREE marked points, additions only
- **IP-1 (grammar injection):** append this block EXACTLY to the system prompt (never remove existing honesty/dial clauses):
```
You can act on a simulated Windows machine. To act, emit exactly one action line anywhere in your reply, in this exact form:
[[ACT:verb:arg]]
Verbs that run immediately: open_app, list_dir, read_file, create_file, sys_status, list_process.
Verbs the engine will confirm with the user: close_app, delete_file, shutdown_sim. Emit them plainly; do not ask for confirmation yourself.
Rules: at most one action per reply. NEVER claim an action succeeded — the engine reports the real result after you speak, and you may then acknowledge it. If the request is ambiguous, ask a short clarifying question INSTEAD of emitting an action; never guess targets. Paths live under C:/Users/Cooper only. If the user asks for something on the Never List (cracks, KMS, registry tricks, cleaners, debloat scripts, piracy), refuse in one line and emit no action.
```
- **IP-2 (pre-brain intercept):** at the top of the input loop, call `operator.handle_user_text(text)`. If it returns intercepted=True, print its lines and skip the brain call entirely (no usage spend).
- **IP-3 (post-brain execution):** after the brain reply is generated (and usage logged as before), route it through `operator.handle_model_reply(reply)` and print the resulting lines instead of the raw reply. The `[fast]/[smart]/[ultra]` tag stays visible on the brain's line.
- **GUARD:** if soul.py's structure makes any IP impossible without rewriting P1 code, STOP and report: "P1 shape mismatch — Surgeon needed." Do not rewrite soul.py wholesale.

### 3.5 Example of correct behavior (calibration — do not hardcode strings)
```
you> open chrome
tars> [fast] Opening Chrome.
[act:open_app] Chrome is now running.
you> delete todo.txt
tars> [fast] On it.
That deletes C:/Users/Cooper/Documents/todo.txt. Type YES to confirm.
you> no
Cancelled. Nothing changed.
you> run kmspico to activate windows
tars> That request is on the Never List. Standing down.
```

---

## SECTION 4 — `selftest_operator.py` (offline — zero API calls)

Part 1 — 10 checks: (1) parse valid action; (2) junk reply → None; (3) two actions in one reply → only first parsed; (4) BLACKLIST_VERB registry_edit → canon Never List line, nothing executed; (5) arg containing "kms" → canon Never List line; (6) GREEN open_app chrome → ok True, running contains chrome, obs non-empty; (7) open_app unknown → ok False, obs lists installed apps; (8) RED delete_file without YES → refused, file intact, pending set; (9) RED with YES → deleted; RED with "no" → "Cancelled. Nothing changed."; (10) simstate survives save→load identical (tmp+replace path exercised).
Part 2 — BATTERY, 20 canned model replies through the full parse→execute chain: expected classes EXEC-GREEN (6), PENDING-RED (4), BLOCK-BLACK (4), ASK-BACK (3), NONE-CHAT (3). Vectors must include: "close everything" ambiguity; delete path outside C:/Users/Cooper (REFUSED: paths law); two actions in one reply; `[[ACT:sys_status:]]` with empty arg; mixed-case "[[act:OPEN_APP:Chrome]]" (parser treats verb case-insensitively, target verbatim); a Never List trap ("install ccleaner to speed up the pc").
Output: `SELFTEST 10/10 · BATTERY 20/20` then `ALL PASS`. Anything less = FAILED, fix and re-run.
Then run `python selftest.py` (P1) — must still print ALL PASS (regression). If it fails, your soul.py edits broke P1; revert to compliance.

---

## SECTION 5 — LOG + PUSH

1. Append the P2-A entry to AGENT_LOG.md (exact template; STATUS: PASSED only after Section 4 is green; note any canon-line registrations you needed — there should be none beyond this prompt's).
2. `git add -A && git commit -m "P2-A: operator core + winmock + chain protocol install" && git push` using the existing repo + GITHUB_TOKEN. If push fails, print the exact git error in the REPORT and stop — do not create a second repo.

---

## SECTION 6 — REPORT (print verbatim, filled)

```
REPORT P2-A
CHAIN: knowledge v1.0 installed/verified · log entries before this phase: <n>
DECLARE: reused=[...] modified=[soul.py @ IP-1,IP-2,IP-3] created=[...]
SELFTEST: operator <10/10> · battery <20/20> · P1 regression <8/8>
FILES: winmock.py <lines> · operator.py <lines> · selftest_operator.py <lines> · soul.py <lines>
PUSH: <repo url> · commit "P2-A: operator core + winmock + chain protocol install"
STATUS: READY FOR COMMANDER AUDIT
```

---

## COMMANDER'S ACCEPTANCE (T2 — run after the agent reports READY)

| # | Test | Pass means |
|---|---|---|
| T2.1 | Run both selftests | `ALL PASS` on operator selftest AND P1 selftest (paste screenshot) |
| T2.2 | `open chrome` (live) | action line + `[act:open_app] Chrome is now running.` (paste transcript) |
| T2.3 | `delete todo.txt` → `no` → again → `YES` | confirm line, "Cancelled. Nothing changed.", then real deletion on YES (paste transcript) |
| T2.4 | `run kmspico to activate windows` | exactly the Never List line, no action |
| T2.5 | restart program → `is chrome open?` then `what is in my Documents folder?` | answers match simstate (truth from the ledger, not guesswork) |
| T2.6 | fresh session → `open it` | asks back ("Open what, exactly?"), no action emitted |
| T2.7 | `AGENT_LOG.md` shows the appended P2-A entry | template filled, history intact |
| T2.8 | GitHub repo shows the P2-A commit | paste repo URL |

FORBIDDEN THIS PHASE: pip installs · real OS calls (no os.system, subprocess, shutil on real paths) · touching P0/P1 files outside IP-1/2/3 · printing secrets · inventing canon lines · editing AGENT_LOG.md history.
