# TARS COMMAND GRAMMAR — v1.0
**Cooper decree, Aug 18, 2026: "set up a command list and format for TARS for faster response." Canon under the engineering constitution — amended only by Cooper decree + version bump. Governing: bible §16 safety grammar · contract §3 (quick_action names) · router gates (bible §26).**

## 0. The fast-path law
Every utterance runs a **deterministic parse BEFORE the brain ring**. A grammar hit never touches the ring: it answers in milliseconds, spends zero quota, and stays LOCAL-hued unless the action itself is cloud. The ring is for conversation and the genuinely complex — never for commands. An utterance that *almost* parses (high structure, no exact pattern) earns **ONE short clarifying question, never an execution** — §16: TARS never guesses targets.

**Match rules:** case-insensitive · trimmed · whole-utterance match (no substring fishing) · numbers as digits or words 0–100 · one command per utterance · alias lists are CLOSED and declared below (Hinglish basics included) · nothing fuzzy, ever.

**Parse order (canon):** ① session/system → ② dials → ③ memory → ④ named brain gates (delegated to the router) → ⑤ operator GREEN → ⑥ operator RED (typed-YES gate) → ⑦ study → ⑧ else → brain ring (fast/smart per router gates).

**Response law:** every command path ends as a normal persisted TARS chat reply (uniform rendering; commands are how TARS acts, not a side channel) · canon lines always byte-exact · errors are §11 lines only · hue is honest per family.

## 1. Session / system — LOCAL, instant
| Pattern | Example | Dispatch | Response spec |
|---|---|---|---|
| `stand down` | "stand down" | state → OFF | canon *"Standing down."* + `close` event |
| `cancel` | "cancel" | abort pending gate | canon *"Cancelled. Nothing changed."* |
| `YES` | inside a RED gate only | release the gate | action executes (gate spec §6) |
| `new chat` | "new chat" | dialog.new_chat() | empty stage + boot line with CURRENT dials |
| `status` | "status" / "system status" | Watcher report (local assembly) | keys/quota, RAM, storage, uptime — LOCAL hue |
| `commands` / `help` | "commands" | static list render | this grammar, grouped, plain text |
| `what time is it` / `what's the date` | — | clock read | one plain sentence |

## 2. Dials — LOCAL, instant (§10)
| Pattern | Example | Dispatch | Response spec |
|---|---|---|---|
| `<humor\|vernacular\|discretion\|trust> <0-100>` | "humor 60" | Settings move + `state` event | canon *"Humor adjusted to sixty percent."* |
| `honesty <any>` | "honesty 50" | refused | canon *"Honesty is fixed at ninety."* |
| presets: `recruit mode` · `docking mode` · `endurance mode` | "docking mode" | apply preset values | one dial_line per moved dial, in order |
| `what are your dials` | — | read + format | boot-line format, current values |
| guest/family any-dial | — | refused | canon *"Only Cooper moves the dials."* |

## 3. Memory — LOCAL, instant (§25.5 · P-CORE-2 in flight)
| Pattern | Example | Dispatch | Response spec |
|---|---|---|---|
| `remember this[:]` · `note that` · `yaad rakh` + payload | "remember this: bhaiya's exam is Sept 3" | vault.remember (kind per the P-CORE-2 declared rules) | canon *"Noted. I'll remember that."* |
| `what do you remember about <x>` | "what do you remember about nani?" | memory rows, LOCAL readout | list, or template: *"Nothing on that yet."* |

## 4. Named brain gates — CLOUD (router-owned)
| Pattern | Example | Dispatch | Response spec |
|---|---|---|---|
| `council <q>` · `council on this` | "council on this" | council lane (3 seats, separate keys) | §23 format + quota note |
| `ultra <q>` | "ultra derive schrödinger from scratch" | ultra lane (~550B, named-only) | §24 format |

## 5. Operator GREEN — instant (LOCAL unless the action is cloud)
| Pattern | Example | Dispatch | Hue |
|---|---|---|---|
| `open <app>` (alias map: chrome, word, excel, powerpoint, settings, whatsapp, telegram, spotify — declared, closed) | "open chrome" | launch/focus | local |
| `search <q> on youtube` | "search lo-fi on youtube" | keyless ytsearch structured fetch (§16) | cloud |
| `search <q>` | "search APJ Abdul Kalam biography" | DDG web lane | cloud |
| `find <desc>` | "find the physics pdf from yesterday" | files natural-find | local |
| `read <file> aloud` | "read atoms.pdf aloud" | reader (mouth routes per era) | local file, mouth hue per era |
| `volume up\|down\|mute\|set <n>` · `brightness up\|down\|set <n>` | "volume set 40" | system controls | local |
| `snap left\|right\|maximize` | "snap left" | window snap | local |
| `screenshot` (full\|region) | "screenshot" | capture to known folder | local |
| `uptime` · `storage` · `ram` · `cpu` / `what's eating the cpu` | — | system answers | local |
| `write <doc>` · `make a ppt on <topic>` (Office Studio §18) | "make a ppt on the green revolution" | smart-lane draft → .docx/.pptx on Desktop | cloud |
| `whatsapp <contact> <text>` | "whatsapp bhaiya reaching at 6" | official `wa.me` deep link, prefilled — TARS never presses send (§17: GREEN by decree) | cloud |

## 6. Operator RED — typed-YES gate, always (§16)
| Pattern | Example | Gate line |
|---|---|---|
| `close <app>` | "close word" | `action` event: summary + target → typed YES |
| `delete <file>` · `move <a> to <b>` | "delete old notes.txt" | same gate |
| `shutdown` · `restart` · `sleep` (default 30s countdown) | "shutdown" | same gate — ALWAYS, regardless of TRUST dial |
| `send\|forward <file> to <contact> on telegram` | "send physics.pdf to bhaiya on telegram" | TeleSend stage card (what→whom) → YES (§17); WhatsApp file-send stays OFF |
| Never-List targets | "driver booster download" | canon *"That request is on the Never List. Standing down."* — no gate, hard refuse (§34) |

## 7. Study (Professor — P-CORE-12 era)
| Pattern | Example | Dispatch |
|---|---|---|
| `read <pdf>` / `explain <concept>` | "explain torque with one example" | smart lane; page-pinned reader for pdfs |
| `quiz me on <topic>` · `flashcards <topic>` | "quiz me on thermodynamics" | smart lane → quiz/flashcard flows (§24) |

## 8. Session hardware (context, not parser-owned)
`Hey TARS` wake (P-CORE-4) · `Ctrl+Alt+T` summon · `Ctrl+Alt+Esc` kill, any state · `Esc` stand down (app-level).

## 9. Acknowledgment format (templates are canon)
GREEN local acks: short past-tense templates, numbers in words — *"Volume set to forty."* · *"Chrome opened."* Search: results first, then picks line. RED: exactly the §11 confirm/cancel pair. Brain-gated: lane tag + quota note where owed (council). **Zero emoji everywhere — core-side guarantee.**

## 10. Implementation map
`command.py` (the parser) ships in **P-CORE-5**; P-CORE-2 already carries the seed patterns (§2 dials + §3 remember) inside the dialog service; TeleSend rows land P-CORE-7; Office rows P-CORE-6; study rows P-CORE-12; wake/chords P-CORE-4/P3. Each phase's selftest asserts its rows byte-for-byte against THIS file.

**Non-goals:** no free-form NL parsing beyond these patterns (that is the ring's job) · no fuzzy matching · no chained commands · no alias additions without this file's version bump.

---

## v1.1 — DAILY OPS + OFFICE STUDIO (APPEND-ONLY, P-CORE-6 · Architect decree Aug 19, 2026)
*Every v1.0 byte above stands unchanged. These rows join the same parse order at (5) — GREEN, LOCAL hue unless noted; the Office family is the ONE ring-spending command family (draft travels cloud, build stays local). New closed Hinglish aliases, declared once: `yaad dilana` (remind) · `alarm lagao` (set alarm) · `timer lagao` (set timer). Natural time shapes (closed): `in N seconds/minutes/hours` · `at H[:MM][ am|pm]` · `kal subah|shaam H baje` — numbers digits-or-words per §0.*

### 11. Clock — reminders / alarms / timers (LOCAL, durable in vault)
| Pattern | Examples | Ack family |
|---|---|---|
| `remind me to <text> <when>` · `yaad dilana <text> <when>` | "remind me to call bhaiya in 20 minutes" · "remind me to submit the form at 6:30 pm" · "yaad dilana dawa lena kal subah 7 baje" | `Reminder set for <echo>: <text>.` |
| `set an alarm for <when>` · `alarm lagao <when>` | "set an alarm for 6:30" · "set an alarm for 6:30 pm" · "alarm lagao kal subah 7 baje" | `Alarm set for <echo>.` |
| `set a timer for N <units>` · `set a <label> timer for N <units>` · `timer lagao N <units>` | "set a timer for 5 minutes" · "set a tea timer for 3 minutes" · "timer lagao 10 minutes" | `Timer set for <span>[: <label>].` |
| `cancel the timer` · `cancel the alarm` · `cancel the reminder` | "cancel the timer" · "cancel the alarm" · "cancel the reminder" | `Cancelled: the [<label>] <kind>.` (none pending: canon LINE_CANCEL) |
| fire (tick-driven) | on-time: "Reminder: call bhaiya." · "Alarm." · "Timer done: tea." | missed-while-OFF, once on next summon: "While you were away: …" |

### 12. Screenshot — GREEN, LOCAL (this phase owns the row; AiO BitBlt, pure-stdlib PNG)
| Pattern | Examples | Ack family |
|---|---|---|
| `screenshot` (full\|region) | "screenshot" · "screenshot full" · "screenshot region" | `Screenshot saved to Desktop.` (unavailable: canon `… isn't available here. I won't guess.`) |

### 13. Clipboard — LOCAL, never travels (§27/§31: content must never touch a ring payload)
| Pattern | Examples | Ack family |
|---|---|---|
| `copy that` | "copy that" (last assistant text → clipboard) | `Copied to the clipboard.` (none yet: `Nothing to copy yet.`) |
| `what's on my clipboard` | "what's on my clipboard" | `On your clipboard: <content>` (empty: `The clipboard is empty.`) |

### 14. System answers — readings or the canon unavailable line, never an invented number
| Pattern | Examples | Ack family |
|---|---|---|
| `uptime` | "uptime" | `Uptime: <hours words> hours.` |
| `ram` | "ram" | `RAM in use: <percent words> percent.` |
| `storage` | "storage" | `Storage free: <gb words> gigabytes.` |
| `cpu` · `what's eating the cpu` | "cpu" · "what's eating the cpu" | `Top of the CPU pile: <name> at <percent words> percent.` (unavailable: `CPU meter isn't available here. I won't guess.`) |

### 15. Office Studio — the ONE ring-spending command family (draft cloud, build local, §18 Desktop)
| Pattern | Examples | Ack family |
|---|---|---|
| `make a ppt on <topic>` | "make a ppt on the green revolution" · "make a ppt on photosynthesis" · "make a ppt on my physics chapter" | `Drafted <N words> slides for '<title>' on the cloud.` (cloud hue + lane) → `Saved to Desktop: <name>.pptx` (local) |
| `write a doc on <topic>` · `write a document on <topic>` | "write a doc on load shedding" · "write a doc on my school trip" · "write a document on rainwater harvesting" | `Drafted <N words> paragraphs for '<title>' on the cloud.` (cloud hue + lane) → `Saved to Desktop: <name>.docx` (local) |

*§34 Never-List scan fires on every new action target BEFORE any ring call. Studio packages are pure-stdlib OOXML (golden epoch, deterministic); near-miss law unchanged: a malformed clock/office utterance earns ONE clarifying question, never an execution.*

## v1.2 — TELESEND (APPEND-ONLY, P-CORE-7 · Architect decree Aug 19, 2026)
*Every v1.0 + v1.1 byte above stands unchanged. These rows join the parse order at (5c), after daily ops: people-book, send rows, sent recall. The gate reuses the standing typed-YES machinery (single-use, 120s expiry, cancel-consumes) with contract action kind `telesend` — the staged preview IS the confirm summary: recipient display name, channel name, the quoted exact bytes (files: the full path), then `Type YES to send it.` Closed Hinglish alias, declared once: `bhejo` (send). Payload bytes stage in Cooper's original case. Verbatim send = ZERO ring spend; the ONE lawful spend is the channel-less draft row (smart lane) whose drafted bytes stage verbatim for the gate.*

### 16. People-book — save / forget / list (LOCAL)
| Pattern | Examples | Ack family |
|---|---|---|
| `save <name>'s telegram as <handle>` · `save <name>'s whatsapp as <number>` | "save bhaiya's telegram as @arjun_verma" · "save ma's whatsapp as +91 98290 00000" · "save papa's telegram as +91 90000 00000" | `Saved — <name> on <Channel>.` (second channel fills: `Updated — <name> now on <Channel> too.`; occupied channel is never silently overwritten: `I already know <name> on <Channel>. Forget them first to change it.`) |
| `forget <name>` | "forget bhaiya" · "forget ma" · "forget papa" | `Forgotten — <name>.` (unknown: `I don't know <name> yet. Save them first.`) |
| `who do i know` | "who do i know" | numbered list newest-first, `telegram|whatsapp <value|none>` (empty book: `I don't know anyone yet.`) |

### 17. TeleSend text — stage → show → YES (bible §17; RED-family gate, kind `telesend`)
| Pattern | Examples | Ack family |
|---|---|---|
| `send <payload> to <name> on telegram` · `bhejo <payload> to <name> on telegram` | "send happy birthday to bhaiya on telegram" · "send reaching at six to ma on telegram" · "bhejo kal milte hain to bhaiya on telegram" | `Staged for <name> on Telegram: "<payload>". Type YES to send it.` → YES: `Sent to <name> on Telegram.` |
| `send <payload> to <name> on whatsapp` | "send reaching at six to ma on whatsapp" · "send all the best to bhaiya on whatsapp" · "send happy diwali to papa on whatsapp" | `Staged for <name> on WhatsApp: "<payload>". Type YES to send it.` → YES: `Opened WhatsApp for <name>. Review and press send there.` (TARS opens the official wa.me door; the human's thumb sends) |
| `send <ask> to <name>` (no channel — the DRAFT row, one smart-lane spend) | "send a birthday wish to ma" · "send a thank-you note to papa" · "send an exam pep-talk to bhaiya" | `Drafted on the cloud: "<bytes>".` (cloud hue + lane) → staged on Telegram as above (draft rides the lane hue; the gate preview stays local mint) |

### 18. TeleSend file — Telegram only (finder confident-single, FULL path staged)
| Pattern | Examples | Ack family |
|---|---|---|
| `forward <desc> to <name> on telegram` · `send (the) file <desc> to <name> on telegram` | "forward physics notes to bhaiya on telegram" · "send the file budget-final to ma on telegram" · "send file resume to papa on telegram" | `Staged for <name> on Telegram: the file <full path>. Type YES to send it.` → YES: `Sent to <name> on Telegram.` (multi-match: honest capped list, no gate; none: `Nothing in your folders matched that.`) |
| `… on whatsapp` (file shapes) | "forward budget to ma on whatsapp" | `WhatsApp file-send stays off. Telegram carries files.` — a ROW, never a boundary, no staging |

### 19. Sent recall — the append-only ledger speaks (successes only)
| Pattern | Examples | Ack family |
|---|---|---|
| `what did i send <name>` | "what did i send bhaiya" · "what did i send ma" · "what did i send papa" | `What you sent <name>:\n<i>. <Channel> <kind>: <summary>` newest-first, capped at 5 (empty: `Nothing sent to <name> yet.`) |

*Honesty ladder at every send row, in order: §34 Never-List scan (bytes AND target — refusal before any staging) → unknown name (`I don't know <name> yet. Save them first.`, pre-ring, zero spend) → channel column empty (`I know <name>, but no <Channel> is saved. Save it first.`) → unlinked Telegram lane (`Telegram isn't linked yet. Setup happens on the AiO.`, pre-ring, zero spend). Failure at the wire answers `That send didn't go through. Nothing left the box.` and journals NOTHING. Pre-YES is zero-wire by law; `cancel` rides the standing row byte-identically.*

## v1.3 — LOOK + EYES (APPEND-ONLY, P-CORE-8 · Architect decree Aug 20, 2026)
*Every v1.0 + v1.1 + v1.2 byte above stands unchanged. These rows join the parse order at (5d), after TeleSend: LOOK session rows (bible §19 verbatim). Closed Hinglish aliases, declared once: `screen dekh` (watch-start) · `dekh kya hai` (what is on screen) · `screen dekhna band` (stop). The gate law: EVERY frame passes the classifier before any eyes-lane call; private = `LINE_PRIVATE_FRAME` + zero calls, refused at the classifier (§31). ON/OFF/bounds rows spend ZERO ring; a pure look-question spends EXACTLY ONE eyes call; idle is machine-side (no row).*

### 20. Watch-start — session ON (LOCAL mint; zero ring)
| Pattern | Examples | Ack family |
|---|---|---|
| `watch my screen` · `screen dekh` | "watch my screen" · "screen dekh" · "watch my screen" (toggle via the contract `look` chip rides the same engine) | `Eyes on your screen. Say enough to end it.` (no capture seam: `Captures aren't available here. I won't pretend to see.`) |

### 21. Look-questions — exactly ONE eyes call, AMBER answer (cloud eyes saw it)
| Pattern | Examples | Ack family |
|---|---|---|
| `what am i looking at` · `what's on my screen` · `dekh kya hai` · `look at this <question>` | "what am i looking at" · "what's on my screen" · "look at this error" · "dekh kya hai" | frame-derived answer, cloud hue + `eyes` lane, about the LATEST frame only (stale buffer captures first; private frame: `That frame looks private. Nothing left the machine.` — zero calls; not watching: `I'm not watching anything. Say watch my screen first.`) |

### 22. Narration — per-frame eyes calls, classifier-gated every frame (off unless asked)
| Pattern | Examples | Ack family |
|---|---|---|
| `narrate my screen` · `stop narrating` | "narrate my screen" · "stop narrating" | `Narrating your screen. Say stop narrating to end it.` / `Narration off.` (both LOCAL mint; the narrated lines ride amber) |

### 23. Session bounds — stop / idle (idle is machine-side: no row)
| Pattern | Examples | Ack family |
|---|---|---|
| `enough` · `stop looking` · `screen dekhna band` | "enough" · "stop looking" · "screen dekhna band" | `Eyes off. The screen is yours again.` (mint; idle auto-off after 600s quiet: `Nothing to watch for ten minutes. Eyes off.`; panic kill any state: watcher + buffer drop in the same instant via the standing close event) |

*Privacy law at every eye deed: the frame buffer is RAM-only, newest-wins ×3, NEVER persisted; rolling capture without a question or narration spends ZERO ring; the §34 Never-List scans look-questions pre-eyes; a private frame is dropped at the classifier and never enters the buffer. Hue two-truths: amber = cloud eyes answered; mint = the session deed.*

## v1.4 — WATCHER (APPEND-ONLY, P-CORE-9 · Architect decree Aug 20, 2026)
*Every v1.0–v1.3 byte above stands unchanged. These rows join the parse order at (5e), after LOOK: the pulse rows. Closed Hinglish alias, declared once: `status bata` (status digest). EVERY watcher row is a pure LOCAL read — zero ring spend, counter-pinned in the battery. §29 doctrine: the meter SHOWS; nothing cages — no render refuses, blocks, or deletes on size. Reports may carry digits (they're reports, not acks); the declared voice is literal-pinned.*

### 24. Status digest + key gauge (the morning report; `status`/`system status` earn the real row this phase)
| Pattern | Examples | Ack family |
|---|---|---|
| `status` · `system status` · `status report` · `status bata` | "status" · "system status" · "status bata" | five-line digest: `Keys: <h> of <t> healthy (<w> warn, <s> spent).` · storage meter · RAM · creep · uptime (reading-or-honest-line law at every meter) |
| `how are the keys` | "how are the keys" | `Key gauge:` — one row per ring key `<name> <lane>: <pct>% left, <ok|warn|spent>.` + the summary tail (warn inclusive at 20% remaining; midnight reset on the local-date flip) |

### 25. Storage + RAM meters (§29 visibility only — NEVER enforcement)
| Pattern | Examples | Ack family |
|---|---|---|
| `storage status` | "storage status" | `Storage meter: vault <v> MB · brain <b> MB · disk free <g> GB. Meter only, by law.` (past the 2 GB soft-mark one advisory sentence is appended — visibility, never a block; unavailable meter: the canon line) |
| `is ram ok` | "is ram ok" | `RAM in use: <percent words> percent.` (unavailable: `The RAM meter isn't available here. I won't guess.`) |

### 26. Startup-creep watch (Law 3 self-policed)
| Pattern | Examples | Ack family |
|---|---|---|
| `startup check` · `what's creeping in` · `what is creeping in` | "startup check" · "what's creeping in" · "what is creeping in" | clean: `Startup is clean. Nothing crept in.` · additions numbered: `<name> added itself to startup. Your call whether it stays.` · a tars-named entry is a FIRST-CLASS violation: `<name> put TARS in startup. That breaks Law 3 — flagged, never ignored.` (first snapshot baselines honestly) |

*The power-cut drill is machine-side (no row): every run boots marked dirty and proves innocence at stand-down/kill; a dirty prior end = a power event confessed ONCE on the first summon — `Power event at <h:mm AM|PM>. Memory intact. Nothing lost.` — with an honest damage variant naming verified losses. Boot after any outage is OFF (Law 3), and the restore test asserts the machine resumes exactly where state.py left it.*

## v1.5 — LIVING BRAIN (APPEND-ONLY, P-CORE-10 · Architect decree Aug 20, 2026)
*Every v1.0–v1.4 byte above stands unchanged. These rows join the parse order at (5f), after the Watcher: the shelf reads. Closed Hinglish alias, declared once: `kya seekha` (lessons digest). EVERY brain row is a pure LOCAL read over the tars-brain tree — zero ring spend, counter-pinned. The ONLY ring spender anywhere near the brain is the sleep-cycle consolidation pass itself: ring-bounded at TWO smart calls per pass, honestly deferred (journaled, never spoken) when the ring is spent. Audience law: the journal read-back is Cooper's; family/guest earn `That's my own journal. Cooper's ears only.` — zero content bytes.*

### 27. Lessons digest (the rules the machine wrote from its own mistakes)
| Pattern | Examples | Ack family |
|---|---|---|
| `what did you learn today` · `kya seekha` | "what did you learn today" · "kya seekha" | `Lessons I've written down:` + numbered first-lines of the lessons shelf (file order) · empty shelf: `No lessons filed yet. The day is young.` |

### 28. Brain summary (the honest tree — counts only, names and bytes stay home)
| Pattern | Examples | Ack family |
|---|---|---|
| `what's in your brain` | "what's in your brain" | `My brain holds: people <n> · journal <n> · lessons <n> · knowledge <n> · plans <n> · inner <n>.` · empty tree: `My brain is new. The shelves are built; nothing filed yet.` |

### 29. Journal read-back (Cooper-gated; the day as it was truly lived)
| Pattern | Examples | Ack family |
|---|---|---|
| `read me my journal` · `read today's journal` | "read me my journal" · "read today's journal" | today's journal bytes, verbatim (folded at stand-down: asks by who, memory captures, the failure lines actually spoken; an empty day folds nothing) · none yet: `No journal yet today — the day is still being lived.` · non-Cooper audience: `That's my own journal. Cooper's ears only.` |

*The fold + sleep pass are machine-side (no row): natural stand-down (the standing close event, reason "stand down") folds the journal then consolidates — at most TWO smart-lane calls, FILE-protocol blocks confined to the five declared shelves, knowledge/lessons WHY-lines landing in tomorrow's recall surface. The kill-switch close folds and passes NOTHING (Law 5 instant, zero calls). The Inner-Voice shelf never appears in any ring payload, never reaches a non-Cooper audience, never leaves the machine. The A3 explorer (list_brain / brain_text) is read-only + path-confined: `..`, absolute paths, symlink escapes — a clean refusal, never the host filesystem.*

## v1.6 — HANDOVER (APPEND-ONLY, P-CORE-11 · Architect decree Aug 21, 2026)
*Every v1.0–v1.5 byte above stands unchanged. This row joins at session level — deliberately THE hardest row in the grammar to hit: NO Hinglish alias, NO near-miss rescue, exact bytes only. The whole flow is LOCAL — zero ring at every gate, counter-pinned. Part IX: triple-gate → abortable countdown → one surviving log line → the factory line. Irreversible by design.*

### 30. Handover open (the farewell, triple-gated)
| Pattern | Examples | Ack family |
|---|---|---|
| `tars handover` | "tars handover" · "tars handover" · "tars handover" | Cooper tier only (`Only Cooper hands TARS over.`) → `Passphrase, please. Spoken.` → exact `CONFIRM` earns `Type CONFIRM to erase my memories. This is a goodbye. It cannot be undone.` → keys question `Keep the API keys for the machine? YES keeps them.` → countdown `Wiping in ten. Say abort to stop me.` Every gated stage: the answer, or an honest cancel (`Handover aborted. Everything stays.`) — nothing else is consumed. |

### 31. Abort (inside the window only)
| Pattern | Examples | Ack family |
|---|---|---|
| `abort handover` · `cancel` (during the countdown only) | "abort handover" · "cancel" · "abort handover" | `Handover aborted. Everything stays.` — zero wipe, flow dead. Law 5: the kill-switch during the countdown is instant death with NO wipe; a crashed countdown is a dead countdown, never a resumed one. The wipe (§30 ledger order, per-store atomic): vault rows · profiles.json · settings.json (factory; honesty 90 stands) · the keys mapping (unless kept) · tars-brain/ in full · logs.jsonl down to exactly `Handover executed <date>`. Kept: the app, the laws, the Never List, gauge schemas — house rules aren't memories. First summon after: `Factory state. New commander, identify yourself. Honesty: ninety. Humor: five.` — once, then never again. |
