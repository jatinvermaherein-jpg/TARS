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
  ① PC OPERATOR (the hands) — launch/close apps, volume/brightness, window snap, screenshots, file find, clipboard, reminders, system answers, power intents. Destructive or irreversible ALWAYS requires explicit confirmation; ambiguous requests get asked back, never guessed. (Built SIMULATION-FIRST in P2-A; real OS binding in P3.)
  ② VOICE COMPANION (the soul) — free chat with real memory, live dial obedience, barge-in.
  ③ SYSTEM WATCHER (the medic) — key gauge panel, health intents, morning report, power-cut drill (crash-safe resume, boot-to-OFF after outage, damage report on first summon).
  ④ STUDY PROFESSOR (the tutor) — PDF explain/quiz, spaced repetition, physics-mentor mode (Class 11 -> PhD horizon), ultra lane for rare deep problems.
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
