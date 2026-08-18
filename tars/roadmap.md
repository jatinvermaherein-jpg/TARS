# TARS MASTER ROADMAP — App-Era, Two-Lane Build
**v1.1 · August 17, 2026 · Supersedes all previous phase maps · Governing docs: bible v1.2 (`tars-definition.md`) + `bridge-contract.md` v1.4. If this file conflicts with the bible, the bible wins.**

---

## 1. The crew (new org chart — Cooper decree Aug 17)

| Role | Who | Duties |
|---|---|---|
| **Architect-Operator** | Arena agent (this seat) | Writes every prompt, owns roadmap/spec/contract, audits reports, merges decisions, keeps corpus clean |
| **Delivery** | Cooper | Creates the repo + deploy keys on GitHub · pastes prompts into the agents · brings report blocks back · performs machine-day physical rituals (enrollment, audition, drills) · ~20 min sessions, phone-first |
| **AGENT CORE** | Arena AI (main agent) | Builds `tars/core/` — the Python soul |
| **AGENT APP** | Arena AI (Battle Mode) | Builds `tars/app/` — the Bridge app static bundle |

## 2. Repo & key protocol (Aug 17 decree: SSH keys, new clean repo)

- **Repo:** brand-new **private** repo `TARS` under account `jatinvermaherein-jpg` (created by Delivery, Aug 17) — empty start (no README/license template). Old `tars-vault` (sumanagra06-wq) = museum, never deployed from again.
- **Auth: three SSH deploy keys** (ed25519, already minted by the Architect): `tars-architect` · `tars-core` · `tars-app`. Delivery adds them at **Repo → Settings → Deploy keys → Allow write (✓)**. **No PAT flying around anymore — GITHUB_TOKEN is retired from the plan.**
- Deploy keys are **repo-scoped**: worst case = this repo only, revocable in one click. Private halves live ONLY in each lane's sandbox `~/.ssh/`, never in the repo, never in chat.
- **SSH-over-443 config** (sandboxes often block port 22 — every agent sets this first):
  `~/.ssh/config` → `Host github.com / HostName ssh.github.com / Port 443 / IdentityFile ~/.ssh/tars_<lane>` → `git remote set-url origin git@github.com:jatinvermaherein-jpg/TARS.git`
- **`.gitignore` from commit #1:** `.env` · `__pycache__/` · `*.pyc` · `tars-ssh/` · `uploads/` · nothing else exotic.
- **Bootstrap:** Architect seeds the corpus (bible v1.2 · contract · roadmap · demo script · prompts · brand assets · knowledge · agent-log) as the first push. Lanes then `git clone` and never see stale docs.
- **Push ritual (both lanes, every phase):** commit message `[LANE] PHASE — one-line truth` → push → paste REPORT block to Delivery.

## 3. The Strict-Prompt Doctrine (no-dead-code law — verbatim in every prompt)

1. **Whole files only.** A phase delivers complete, runnable files. No diffs against files the agent was never shown; no "insert after line 40".
2. **Jurisdiction:** CORE writes only `tars/core/` · APP writes only `tars/app/`. Shared docs are read-only.
3. **Zero dead code:** every import used · every function called by the phase's demo/selftest path · zero TODO/placeholder/stub comments · zero commented-out code · zero "future hook" scaffolds. If nothing executes it, it doesn't ship.
4. **Contract compliance:** APP never invents bridge methods; CORE never invents UI behavior. Both read `bridge-contract.md` before writing a line and re-read it before pushing.
5. **Proof, not claims:** every phase ends with a **selftest that exercises everything shipped**, run by the agent, output pasted verbatim. Blocks: `FILES` (paths + line counts) · `SELFTEST OUTPUT` (verbatim) · `CONTRACT CHECK` (one line per law: pass/fail) · `KNOWN LIMITS` (honest).
6. **Never List + 7 Laws** apply to agents as much as to TARS. Art laws: zero emoji in UI/replies; Cooper's images only, crop/scale only.
7. **Python target: 3.12, Windows-first code** (sandbox is Linux — write Windows-correct: `pathlib`, no hardcoded `/`, win32 APIs behind `if os.name == "nt"` adapters marked with canon line comments, SAPI/pywebview guarded so selftests pass headless).

## 4. Capability ledger — what Arena AI can actually build (the honest answer, Cooper)

| Layer | Agent-buildable? | Note |
|---|---|---|
| Bridge app (entire UI, all panels, mock demo) | **100%** | Pure static engineering; fully testable in-browser via mock |
| State machine · dials engine · vault.db · logs · settings · handover logic | **100%** | Pure Python, selftest-provable headless |
| 8-key router · gauge · adapters · canon error lines | 100% code · **real-call smoke on AiO** | Sandbox uses mock adapters; first live cloud call = P3 ceremony (keys never enter the sandbox) |
| Operator verbs (apps/files/system/screenshot/clipboard/search) | ~95% | Windows APIs coded + mocked; final feel verified on AiO |
| Ears (whisper) · Mouth (SAPI/Piper/edge-tts) · Wake (Porcupine) | ~90% | Code complete + fixture-tested; **mic/latency reality-check on AiO** |
| Cooper ID voice engine (resemblyzer, 16-row matrix) | ~90% | Logic complete; **threshold calibration needs Cooper's real voice** |
| TeleSend · Office Studio · LOOK · Watcher · Living Brain · Council | 95–100% | Telethon needs Cooper-Once login on AiO; LOOK/classifier mocked in sandbox |
| pywebview host integration | 100% code | **True WebView2 behavior only on Windows AiO = Merge Day** |

**Bottom line ~90%:** everything get *written and evidence-proven* by the two Arena lanes; what waits for the machine is physical ceremony (voice enrollment, voice audition by ear, UPS pull-plug drill, mic/cam wiring) and first-live-key smoke. Nothing is "hope it works on delivery day" — every phase carries its selftest.

## 5. Phase map — APP lane (Battle Mode) · all static, zero secrets

| Phase | Ships (covers bible) | Exit gate |
|---|---|---|
| **P-APP-0** Bridge shell + mock | Full §13 anatomy (sidebar/stage/input/voice strip) · 5 states · palette §14 exact · zero-emoji · mock.js implements entire §3 bridge API · canon lines verbatim — **a living demo in any browser** | Demo script scenes 1–10 pass in mock · palette/zero-emoji/geometry audit green · REPORT block |
| **P-APP-1** Conversations | Chat history list · streaming chunks · hover actions (copy/read-aloud/redo stubs into bridge) · empty state (walk-art + boot line) · Esc/stand-down behavior | Demo + multi-chat flow selftest |
| **P-APP-2** Settings app-page | Dials panel (HONESTY locked slider + canon refuse) · Voice ID panel · **Key gauge panel (8 quotas)** · Privacy (hue legend) · Memory explorer (mock `tars-brain/` tree) · System · About | Panels live against mock; no placeholder text |
| **P-APP-2.5** Mission Display v2 reskin (decreed + ratified Aug 17) | Style-only swap to skin v2: 15 tokens + 2 on-accent + 4 alpha utilities · soft-round geometry · soft-glass depth · v1 hex purge (byte-grep gate) · ZERO behavior change | 146 prior checks green + skin guards (v2 present / v1 absent, byte-level) · full screenshot re-sweep (11 shots) · REPORT block |
| **P-APP-3** Operator surfaces | Chip-row flows · red-verb confirm modal (typed-YES) · TeleSend stage card (what→whom→YES) · LOOK banner (WATCHING + amber) · file/result cards · keyboard map (Ctrl+Alt+T etc. shown in-page) | Contract §7 checks 1–8 all pass in mock → **APP FROZEN for merge** |

## 6. Phase map — CORE lane (main agent) · needs 8-key secrets sitting before P-CORE-1

| Phase | Ships (covers bible) | Exit gate |
|---|---|---|
| **P-CORE-0** Skeleton + state machine | `tars/core/` spine: settings.json (dials, honesty-locked) · vault.db (SQLite append-only, crash-safe) · logs.jsonl · state machine (OFF→ARMED→…→OFF, kill-switch) · headless `--demochat` with mock brain · summon/stand-down/idle-OFF | Selftest: full demo script headless green · crash-safety test (kill -9 mid-write, zero corruption) |
| **P-CORE-1** Brain ring | 8-key rotation (Groq×6 fast/smart/eyes/ears lanes · OpenRouter×2 ultra/council) · 3-gate router · 30s-timeout/retry-once · per-call ledger · 80%-warn · canon fail lines (§11) · mock adapters + fixtures | Router unit selftest: rotation, budget-skip, all-spent line, tagged lanes |
| **P-CORE-2** Persona + memory | System-prompt builder (dials live · honesty clauses verbatim §12) · vault memory read/write · "remember this" flows · guest register logic | Selftest: dial moves change outputs; honesty refusal byte-exact |
| **P-CORE-3** Ears + Mouth | whisper-small local (fixture WAV test) · Groq whisper fallback · VAD · SAPI→Piper→edge-tts ladder with privacy routing (edge = never private §27/§31) | Fixture transcripts byte-compare · ladder-fallback selftest |
| **P-CORE-4** Wake + Cooper ID | Porcupine "Hey TARS" · resemblyzer embeddings · enrollment wizard data flow · **16-row error matrix (all rows scripted §22)** · passphrase path | Matrix selftest: all 16 rows triggered with fixtures |
| **P-CORE-5** Operator core | GREEN/RED grammar + typed-YES bridge events · Never-List target-scanner (§34) · app control · files natural-find · system controls · yt-dlp ytsearch + DDG web lanes | Grammar selftest: guess-refusal, cancel canon, red-verb gate round-trip |
| **P-CORE-6** Daily ops | Screenshots · clipboard recall · reminders/alarms/timers · system answers (uptime/RAM/storage/CPU hog) · Office Studio docx/pptx → Desktop (§18) | Golden-file docx/pptx selftest |
| **P-CORE-7** TeleSend | USER lane Telethon (login-once session) · BOT lane elective · WhatsApp wa.me text lane (file-send OFF) · stage→show→YES gate (§17) | Selftest against Telethon in dry-run/mock; gate flow verbatim |
| **P-CORE-8** LOOK + eyes | Rolling captures 3–5s · session bounds (stop/panic/idle) · private-doc classifier pre-send · scout lane calls · WATCHING indicator events | Classifier fixture battery (private = refused at classifier, §19/§31) |
| **P-CORE-9** Watcher | 8-key gauge live · storage meter (visibility only §29) · RAM pressure · startup-creep · **power-cut drill** (boot-OFF + survival report line §32) | Gauge math selftest · drill state-restore test |
| **P-CORE-10** Living Brain | `tars-brain/` tree (people/journal/lessons/plans) · self-curation + sleep-cycle consolidation pass · Inner-Voice private journal (§25.5) · ring-bounded thinking | Consolidation selftest: journal folds → profiles update → tomorrow's recall |
| **P-CORE-11** Privacy + social | Audience-tier enforcement on every personal answer (§31) · edge-tts audience rule · guest mode regression net · **Handover triple-gate + wipe semantics (Part IX)** | Wipe selftest: only `Handover executed <date>` survives; factory boot line |
| **P-CORE-12** Professor + Council | PDF read-aloud/explain · quizzes · flashcards · ultra-lane named-summon (§24) · Council parallel answers + verdict (§23) | Quota arithmetic selftest (council = 2–3× flagged) |

## 7. Convergence & machine days

| Milestone | Content | Gate |
|---|---|---|
| **P3 — MERGE DAY (on the AiO)** | Core host loads `tars/app/` via pywebview · `tarsBridge` live wiring · **10-check smoke test (contract §7)** · **FIRST LIVE CLOUD CALL ceremony** (keys from AiO `.env`, never sandbox) | All 10 checks pass verbatim |
| **M-1 Install day** | Python 3.12 · staged pip table · C:\TARS spine · no-auto-start law audit · chords + wake live | Guide checklist sign-off |
| **M-2 Voice ritual** | Voice audition (shortlist, Cooper's ear decides) · enrollment 5×3 rounds + threshold calibration + passphrase | Cold-day borderline / stranger reject proven |
| **M-3 UPS drill** | Pull-plug mid-conversation → survival report on next summon | Canon line + intact vault |
| **GO-LIVE** | Day-one play sheet → monthly ritual (spec) | Cooper declares: "TARS online" |

## 8. Prompt shipping schedule
Architect ships prompts **one whole file per phase, on Delivery's request** — batch available now: **P-APP-0** and **P-CORE-0** (this turn). Say "next batch" per lane as phases pass. Every prompt embeds: read-order (bible → contract → this roadmap §3 doctrine pasted in) · files-to-ship · selftest spec · REPORT block format · the 7 Laws + Never List reminder.
