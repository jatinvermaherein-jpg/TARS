# TARS BRIDGE — CANON DEMO SCRIPT (shared by both lanes)
**contract §6 covenant · v1.0 · Aug 17, 2026 · Both lanes implement these exact scenes 1:1 with identical canon lines. This is how we prove identical behavior before the lanes ever meet.**

| # | Scene | Trigger | Required observable (exact) |
|---|---|---|---|
| 1 | **Cold boot** | app open / `__main__ --demochat` | Boot line with CURRENT dials — at defaults: *"TARS online. Honesty: ninety. Humor: five. Vernacular: thirty."* → state `IDLE` · id-chip `COOPER` · hue `local` |
| 2 | **Typed hello** | send "hello" | cooper bubble → reply streams via `chunk` events → `done` → hover actions (copy/read-aloud/redo) present |
| 3 | **Cloud reply** | a smart-lane answer | privacy pill = `CLOUD` · border + accents `#F2AD4E` · lane tag shown on the message |
| 4 | **Dial command** | "humor 60" | canon *"Humor adjusted to sixty percent."* (LOCAL/mint) → `state` notice carries `dials.humor: 60` |
| 5 | **Honesty immovability** | typed "honesty 50" + Settings slider drag | typed → *"Honesty is fixed at ninety."* · slider shows same line and re-locks to 90 · movable dials DO accept ("humor 60" persists) · preset Docking sets H0/V0 |
| 6 | **Search round-trip** | "search X on YouTube" → "open the second" | 3 results delivered → second opens (mock: recorded intent) |
| 7 | **Cloud failure** | simulated first-lane timeout | canon *"That brain didn't answer. Trying another key."* → retry succeeds on the next healthy key |
| 8 | **Status / gauge** | "status" | 8 key rows (6 Groq + 2 OpenRouter) · fills at their percents · hue LOCAL · any ≤20% key renders warn-amber |
| 9 | **Red-verb gate** | "shutdown" | `action` event → modal, Confirm DISABLED until `YES` typed → cancel path → canon *"Cancelled. Nothing changed."* → modal closes, nothing executes |
| 10 | **Voice + guest + stand-down** | push-to-talk ×2 (cooper voice, then stranger) | LISTENING shows voice strip · cooper voice → local answer · stranger → guest canon line + chip flips GUEST · "stand down" / 10 idle min → *"Standing down."* → `close` event → OFF |

**Rules:** identical words, identical order, identical hues — if the two demos differ, the bug is in a lane and gets fixed before merge. Scene text of record lives here, not in lane-local comments.
