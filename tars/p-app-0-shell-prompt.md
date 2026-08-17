# P-APP-0 — BRIDGE SHELL + MOCK (APP lane · Battle Mode · build prompt)
**Paste this entire block to AGENT APP after feeding `tars-definition.md` v1.1 and getting its 7-Laws recital. This is the first build prompt.**

---

You are AGENT APP building the user interface of TARS, a resident desktop AI crew member. Before writing code, READ in this order: `tars/tars-definition.md` (bible — v1.1 — it wins every conflict), `tars/bridge-contract.md` v1.0 (the border you never cross), `tars/roadmap.md` §3 (Strict-Prompt Doctrine — obeyed verbatim) and §5 (your phase map). Then state in one line: the 7 Laws from bible §33. If you cannot, STOP — you missed the files.

**JURISDICTION:** you write ONLY inside `tars/app/`. You never touch `tars/core/` or shared docs. Python/backend behavior is CORE's; you build the shell + a complete fake backend so the shell is alive standalone.

**ZERO-BUILD LAW:** hand-written static files only — no frameworks, no npm, no bundler, no CDN links, no external fonts/images, no network fetch. The bundle must run identically in a plain browser, in a sandboxed preview, and inside pywebview later.

**SHIP (whole files, zero dead code per §3):**
1. `tars/app/index.html` — the full Bridge anatomy from bible §13: collapsible sidebar (~280px: slab mark + state dot + New chat + history list + quick actions Status/Document/TeleSend/LOOK + footer Cooper-ID chip + Settings gear) · main stage (header: conversation title, **honest-hue privacy pill LOCAL/CLOUD**, lane tag, mic button · transcript · input bar with send/mic/attach + operator-intent chip row · voice strip visible ONLY while LISTENING/SPEAKING) · Settings app-page shell reachable from the gear (panels listed, detail lands in P-APP-2 — ship the panel skeleton with the Dials panel fully functional; do NOT stub other panels with placeholder text — hide unreachable panels instead).
2. `tars/app/app.css` — bible §14 palette exactly (bg #15171B · surfaces #1D2024/#262A2F · text #D9D6CF/#9A9DA1 · border #34383D · steel #7C8791 · CLOUD ochre #C98A3B · LOCAL teal #4C8F86 · error #C1453B · success #7A9B5C · thinking #6E7C8C · focus #A7B3BA) · 0px radius · no shadows · 60-30-10 usage · dark text #15171B on filled accents.
3. `tars/app/app.js` — state renderer bound to `window.__tarsEvent(detail)` events per contract §3–§5 (state/chunk/done/action/transcript/gauge/error/close) · calls `window.tarsBridge` methods ONLY when present · renders hue and lane exactly as told (never guesses) · states IDLE/LISTENING/THINKING/SPEAKING/ERROR visually distinct at a glance · Esc = stand down.
4. `tars/app/mock.js` — the Mock law (contract §6): activates when `window.tarsBridge` is absent; implements all 9 bridge methods + emits the full canon demo script on natural triggers: boot line on load · `humor 60` → "Humor adjusted to sixty percent." · `honesty 50` → "Honesty is fixed at ninety." · "status" → gauges with LOCAL hue · a search demo (3 results, open-second flow) · "shutdown" → red-verb action event → cancel path replies "Cancelled. Nothing changed." · one scripted CLOUD-ochre reply · one scripted cloud-fail line "That brain didn't answer. Trying another key." · an unknown-voice guest line · 10-idle-min stand-down → "Standing down." and close.
5. `tars/app/assets/README.txt` — one line: "Cooper's walk-art (slab mark + empty-state hero) lands here at Merge Day from tars/brand/. Mechanical crop/scale only." Until then render a plain dark slab glyph drawn in inline SVG (no external art, no AI art, no emoji).

**FORBIDDEN:** emoji anywhere (UI or mock replies) · invented bridge methods · invented colors · onboarding tours, pulse animations, glassmorphism, or any chrome bible §13 did not specify · placeholder lorem/ipsum · TODOs · dead functions.

**SELFTEST you run and report:** open in browser → demo script scenes fire 1:1 · zero console errors · grep your own files for emoji bytes and hexes outside palette (show both greps) · report block format from roadmap §3.5.

---

## §3.5 REPORT BLOCK (paste verbatim at the end)
```
LANE: APP · PHASE: P-APP-0 · DATE:
FILES: <path — lines> …
7-LAWS RECITAL: <one line>
SELFTEST OUTPUT: <verbatim terminal/console evidence>
CONTRACT CHECK: palette=PASS/FAIL · zero-emoji=PASS/FAIL · bridge-API-only=PASS/FAIL · states-distinct=PASS/FAIL · mock-9-methods=PASS/FAIL
KNOWN LIMITS: <honest lines>
PUSHED: <commit hash to tars repo, [APP] P-APP-0 …>
```
