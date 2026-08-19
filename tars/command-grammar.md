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
