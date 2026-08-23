# TARS BRIDGE CONTRACT — v1.5
**The one file both build agents obey · August 17, 2026 · App-Era, two-lane build**
**If you are an AI agent building any part of TARS: this contract defines the border between AGENT CORE and AGENT APP. Neither side crosses it. When your instinct conflicts with this document, the document wins. To change it requires a Cooper decree plus a version bump plus BOTH agents re-reading it.**

**Amendment A5 (v1.5, Aug 23, Cooper decree "ARCHITECT fixes it now" — Merge-Day seam ruling):** the OFF state gains a REACHABLE WAKE DOOR. §3 surface gains a 14th method: `summon() -> Promise<StateNotice>` — the lawful summon with zero message and zero ring spend (the same OFF→ARMED transition send() performs on a first text; the 'state' event envelope carries the wake). APP law: the closed screen IS the door — it shows "Press Enter to summon.", is a focusable button, click and Enter/Space both call summon(), AND the screen hides on EVERY non-OFF StateNotice (the cover is no longer a one-way street — the stand-down path reopens too). Rationale: merge-day field finding on the AiO — the mock never exercised OFF, so the cover shipped without a handle; the real core's Law-3 OFF made it a dead end (composer unreachable, no summon path). Zero-emoji/copy laws unchanged.

**Amendment A4 (v1.4, Aug 17, Architect-post-ratification, Cooper ballot "v2 locked"):** Mission Display v2 becomes the skin canon. Geometry: soft-round radius 8/12/16px (+ capsule pills, asymmetric 16/8 message bubbles, 9–10px glyph tiles, 18px window shell). Depth: soft-glass — raised surfaces `0 4px 14px rgba(0,0,0,.28)`, floating layers `0 10px 28px rgba(0,0,0,.38)`, 3.5% white vertical sheen on header/input strips and raised cards. Hue tokens: CLOUD = warm amber `#F2AD4E`, LOCAL = mint `#5CD6AE`; on-accent text `#0B0E12` (mint) / `#191207` (amber), never white. **Semantics UNCHANGED — hue still means privacy.** All thirteen v1 hexes are retired; their presence in `tars/app/` is an audit failure. Full token law: bible §14 (v1.2) + `tars/brand/palette-mission-display.md` v2.

**Amendment A3 (v1.3, Aug 17, Architect-post-audit of P-APP-2):** four lanes canonized so no Settings panel is orphaned at merge:
- `quick_action` name space += `enroll_voice` (payload {}); CORE implements the enrollment wizard in P-CORE-4; interim replies use §22 canon lines.
- `list_members() -> Promise<MemberFile[]>` — MemberFile = {name, relationship, tier:'cooper'|'family'|'guest', enrolledOn} — NEVER embeddings. CORE: P-CORE-4.
- `list_brain(path) -> Promise<BrainNode[]>` + `brain_text(path) -> Promise<string>` — BrainNode = {path, kind:'dir'|'file', sizeKb, modifiedDay} — read-only Living Brain explorer. CORE: P-CORE-10.
- StatusReport gains `windowsUpdate: string` (Watcher text). CORE: P-CORE-9.
Until each CORE phase lands, the APP mock may supply equivalents (host.tarsMockPayloads); on a real bridge lacking a listed method, the affected panel MAY hide itself (never stub-render).

**Amendment A2 (v1.2, Aug 17, Architect-post-audit):** `done` events now carry `messageId`. P-APP-1 exposed that APP could only resolve message ids by who+text matching inside open_chat — fragile. A2 removes the guess; APP may keep the fallback until CORE ships messageId in P-CORE-2. Backward compatible (additive field).

**Amendment A1 (v1.1, Aug 17, Architect-issued, Cooper-ratified):** `quick_action` name space extended by TWO: `read_aloud` and `redo` — both with payload `{chatId, messageId}`. Rationale: bible §13 hover actions (copy · read-aloud · re-do) had no contract channel (copy is client-side clipboard; the other two needed the bridge). CORE implements them server-side in P-CORE-2 (persona/voice); APP wires the buttons in P-APP-1.

---

## 1. The two lanes

| Lane | Agent | Builds | Folder jurisdiction |
|---|---|---|---|
| **CORE** | Arena AI agent (main) | TARS main: Python backend — state machine, brain router (8-key ring), operator engine, ears/mouth, Cooper ID, memory vault, Living Brain, Watcher, TeleSend, Office Studio, LOOK | `tars/core/` only |
| **APP** | Arena AI agent (Battle Mode) | The Bridge app shell: the full Windows-app UI as a STATIC bundle — HTML/CSS/JS, zero runtime deps | `tars/app/` only |

**Jurisdiction law:** each agent may read the other's folder but writes ONLY inside its own. Shared read-only ground truth: `tars/tars-definition.md` (bible v1.2+), this contract, `tars/brand/` art assets. Both push to the same private repo (`tars-vault`) via the Chain Protocol, logging to `AGENT_LOG.md` with a `[CORE]` / `[APP]` tag on every entry.

## 2. The zero-build law (APP lane)
The app bundle is **hand-written static files** — `tars/app/index.html`, `tars/app/app.css`, `tars/app/app.js`, `tars/app/assets/`. **No frameworks, no bundler, no npm, no node_modules, no build step — ever.** The AiO never sees Node. If a feature seems to need a library, it doesn't: write the 20 lines by hand. The bundle must run identically in three hosts: ① any plain browser (mock mode, for previews) ② pywebview/WebView2 on the AiO (production) ③ the in-app file preview (sandboxed, no network) — so: no CDN links, no external fonts, no external images, no fetch() to the network. Everything inline or under `tars/app/assets/`.

## 3. The bridge surface (Python exposes → JS consumes)
AGENT CORE exposes one global object on the page: `window.tarsBridge` (pywebview js_api). Every method returns a Promise. APP code must treat a missing `tarsBridge` as "mock mode" (§6) and must never call it directly without that check.

```
send(text)             -> Promise<ReplyResult>     // a typed/said user message
get_state()            -> Promise<StateNotice>     // current state + dials + audience
summon()               -> Promise<StateNotice>     // [A5] wake door: OFF->ARMED, zero spend, zero message
set_dial(name, value)  -> Promise<DialResult>      // name in {humor, vernacular, discretion, trust}; 'honesty' is rejected with the canon line
confirm(actionId, yes) -> Promise<ConfirmResult>   // RED-verb gate answers; yes=false means cancel
voice_ptt(phase)       -> Promise<void>            // phase: 'start' | 'stop' (push-to-talk)
get_status()           -> Promise<StatusReport>    // Watcher report: keys/quota, RAM, storage, uptime
list_chats()           -> Promise<ChatSummary[]>   // sidebar history
open_chat(id)          -> Promise<ChatMessage[]>   // load a conversation
new_chat()             -> Promise<{id}>            // start empty stage (empty-state art + boot line)
list_members()         -> Promise<MemberFile[]>   // [A3] voice member files, never embeddings
list_brain(path)       -> Promise<BrainNode[]>    // [A3] read-only Living Brain tree
brain_text(path)       -> Promise<string>         // [A3] leaf preview text
quick_action(name, payload) -> Promise<ReplyResult> // chips: 'open'|'search'|'find_file'|'document'|'telesend'|'look'|'status'|'council' (+A1: 'read_aloud'|'redo' with {chatId,messageId})
```

### Python → JS events
CORE pushes events by invoking `window.__tarsEvent(detail)` with a JSON object. APP listens; a missing handler function must never crash core (core wraps the call defensively). Event `type` values:

```
'state'   StateNotice   — {state, dials:{humor,vernacular,discretion,trust}, audience:'cooper|family|guest', lane:'fast|smart|eyes|ears|ultra|council|null', hue:'local'|'cloud'}
'chunk'   ReplyChunk    — {chatId, seq, text} streaming pieces of TARS's reply (app appends)
'done'    — {chatId, messageId, hue, lane} reply complete (app finalizes borders/actions)  [A2: messageId added]
'action'  ActionRequest — {actionId, kind:'red-verb', summary, target} confirm gate modal content (typed YES flow per bible §16)
'transcript' — {who:'cooper'|…, text} what the ears heard, shown dimmed above the reply
'gauge'   GaugeDelta     — {keyIndex, lane, remainingPct} key-ring spend update
'error'   {code, line}  — line is ALWAYS one of the bible §11/§22 canon lines, verbatim
'close'   — core is standing down; app plays the exit and closes
```

## 4. Message shapes (both sides, byte-exact semantics)
```
ChatMessage   = {id, who:'cooper'|'tars', text, ts, hue:'local'|'cloud'|null, lane:null|string, actions:['copy','read_aloud','redo']}
ReplyResult   = {chatId}  (content arrives via chunk/done events)
DialResult    = {ok, line}  // honesty attempt -> {ok:false, line:"Honesty is fixed at ninety."}
ConfirmResult = {ok, line}  // cancel -> canon "Cancelled. Nothing changed."
StatusReport  = {keys:[{index,lane,remainingPct,state}], ram:{mb,ceiling:2000}, storage:{vaultMb,brainMb,diskFreeGb}, uptimeS, powerNote:string|null, windowsUpdate:string}  // [A3: +windowsUpdate]
ChatSummary   = {id, title, ts, lastHue}
MemberFile    = {name, relationship, tier:'cooper'|'family'|'guest', enrolledOn}  // [A3] embeddings NEVER cross the bridge
BrainNode     = {path, kind:'dir'|'file', sizeKb, modifiedDay}                    // [A3]
```

## 5. The rendering laws (APP lane owes these)
1. **State machine is core-owned.** `OFF/ARMED/LISTENING/THINKING/SPEAKING/ERROR` — the app NEVER transitions itself; it renders the last `StateNotice`. If the bridge is silent, the visible state is what it was.
2. **Hue law:** accent colors are decided by CORE (the `hue` field) and rendered by APP. Amber `#F2AD4E` = CLOUD, mint `#5CD6AE` = LOCAL. The app never guesses.
3. **Zero-emoji law:** core-side guarantee; app must not add any (no system emoji pickers, no emoticon glyphs). Lucide-class inline SVG pictograms only.
4. **Art law:** only Cooper's supplied assets in `tars/brand/` — mechanical crop/scale only, referenced from `tars/app/assets/` copies made at Merge Day.
5. **Palette:** exact hex from bible §14 (Mission Display v2 — 15 tokens + 2 on-accent + 4 alpha utilities, nothing else). No new colors. On-accent text `#0B0E12` (on mint) / `#191207` (on amber) on filled accents — never white.
6. **Voice strip** exists only while `state` ∈ {LISTENING, SPEAKING} or ptt active.
7. Anatomy/geometry per bible §13 + §14 v2 (A4): sidebar ~280px collapsible · window 1240×780 min 960×620 · soft-round radius 8/12/16 (+ capsules, asymmetric bubbles) · soft-glass depth (restrained shadow + 3.5% sheen — no glow/neon).

## 6. The Mock law (both lanes are independently testable)
- **APP ships `tars/app/mock.js`**: a complete in-browser fake `tarsBridge` — boots with the canon boot line, answers a script of demo interactions (dial command, search demo, red-verb confirm gate, status gauges, cloud-fail error line, guest-voice line), and auto-activates when `window.tarsBridge` is absent. Anyone opening `index.html` in a browser sees a living demo with zero backend.
- **CORE ships a headless self-test**: runs the same JSON shapes in terminal (no app needed) — `python -m tars.core --demochat` replays the same demo script through the real pipeline minus UI. **Merge Day (P3) is the first time the two lanes meet.**
- The demo script is shared canon: `tars/bridge-demo-script.md` — both lanes implement it so demos are comparable 1:1.

## 7. Merge Day smoke test (10 checks, all must pass)
1. Cold open shows empty state + boot line ≤ ~2s · 2. Typed hello → chunked reply + done · 3. Hue pill flips amber on a cloud reply, mint on local status · 4. `humor 60` → canon line + state notice · 5. `honesty 50` → "Honesty is fixed at ninety." slider stays locked in Settings · 6. A red-verb (e.g. "shutdown") → action modal → cancel returns "Cancelled. Nothing changed." · 7. `status` → gauges render from real StatusReport · 8. Wake path: LISTENING state + voice strip visible while speaking · 9. Kill: `Ctrl+Alt+Esc` closes app instantly (RAM back to 0) · 10. Idle 10 min → stand down → app closed.

## 8. Order of work
**APP lane** needs no secrets and no machine — deployable immediately (P-APP-0: shell + mock demo). **CORE lane** needs the 8-key secrets sitting + GITHUB_TOKEN before P0 reap (vault, router). Lanes converge at P3 on the AiO.
*Both lanes obey bible v1.2 absolutely: four roles only, zero-emoji, art laws, Never List, 7 Laws.*
