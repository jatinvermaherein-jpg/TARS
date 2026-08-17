# P-APP-1 — CONVERSATIONS: wiring + streaming + hover actions (APP lane · build prompt)
**Paste to AGENT APP. Prerequisites: P-APP-0 PASS is banked. Re-read `tars/bridge-contract.md` — it is now v1.1 (Amendment A1).**

---

Continuing AGENT APP. Jurisdiction unchanged: `tars/app/` only. Zero-build law unchanged. Re-read contract v1.1 §3 (A1: quick_action gains `read_aloud` and `redo`, payload `{chatId, messageId}`) and `tars/bridge-demo-script.md`. This phase wires everything P-APP-0 rendered statically; the mock must keep all 10 canon scenes green.

**SHIP (whole files, zero dead code):**
1. `tars/app/app.js` — upgrades:
   - **Hover actions become functional:** `copy` → `navigator.clipboard.writeText` of that message's text (+ brief "copied" state on the button, no toast library) · `read_aloud` → `bridge.quick_action('read_aloud',{chatId,messageId})` when bridge present, mock path below · `redo` → `bridge.quick_action('redo',{chatId,messageId})` and the old reply is replaced in place by the new streamed one (thinkable state while streaming).
   - **Streaming smoothing (P-APP-0 known-limit #4 — fix it):** batch incoming `chunk` appends per animation frame; autoscroll only while the user is at the bottom; if scrolled up, show a steel-bordered "jump to latest" pill anchored above the composer (dismiss on click/Esc). No third-party smooth-scroll anything.
   - Conversation list: newest-first, active conversation highlighted by fill-step (§14 surfaces, no borders-as-decoration), switching preserves each chat's scroll position in memory.
   - Keep every P-APP-0 behavior; regression net must prove it.
2. `tars/app/mock.js` — upgrades:
   - Implement `quick_action('read_aloud', …)` in mock: speak the message text via the browser-native `speechSynthesis` (engine default voice — real Piper voice is CORE/P-CORE-3). While speaking, that message's read-aloud button shows SPEAKING-style state and a click again calls `speechSynthesis.cancel()`.
   - Implement `quick_action('redo', …)`: re-streams a DIFFERENT canned reply for the demo scene (vary wording; keep hues/lane tags honest per the original reply).
   - Gauge: 8 rows remain (6 Groq + 2 OpenRouter) per bible §26 current manifest.
3. `tars/app/index.html` — only what the wiring needs (button glyphs already inline-SVG; add nothing decorative).
4. `tars/app/app.css` — jump-pill + button pressed/copied/speaking states, palette-true, 0px radius, no shadows.

**FORBIDDEN:** emoji · off-palette hex · new bridge methods · placeholder stubs · TODOs · dead markup · smooth-scroll/highlight libraries.

**SELFTEST (previous 52 checks all still green PLUS):** copy writes the exact clipboard string · read_aloud starts + cancel works (assert speechSynthesis.speak called with TARS's text) · redo replaces the reply with different text, lane/hue preserved · 200-chunk flood streams without dropped chunks and with ≤2 reflow-heavy frames per batch (assert via batched-append count, not vibes) · jump-to-latest pill appears only when scrolled up and works · scroll position survives chat switching · attach two screenshots (big-reply streaming mid-flight; pill visible state) — screenshots are a gate, per your P-APP-0 lesson.

**REPORT:** §3.5 block verbatim; commit `[APP] P-APP-1 …`.
