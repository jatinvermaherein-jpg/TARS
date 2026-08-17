# 📨 CLAUDE BRIEF #2 — TARS HOME: Full App Design (paste-ready)
**Aug 10, 2026 · How to use:** copy EVERYTHING between the ✂ lines → paste into Claude (add a capable image/design model's input if handy, but text design-spec is what's needed) → paste the reply back to the Architect. Architect converts the winning direction into mockup **v0.3**; Cooper vetoes.

⸻ ✂ COPY BELOW THIS LINE ✂ ⸻

# DESIGN COMMISSION: "TARS Home" — a desktop AI assistant's entire interface
**You have FULL creative authority over the whole interface: layout, composition, theme-execution, motion, typography treatment, screen choreography. Cooper's words: "no boundaries."** The only constraints are the Six Laws below — they exist to protect a 16-year-old's privacy and a family machine's longevity, and they are not negotiable. Everything else — including the current draft's anatomy — is yours to keep, bend, or throw out entirely.

## 0. What you're designing
**TARS Home** — the popup interface of "TARS," a privacy-first, voice-and-text AI assistant living on a family desktop in India. Named after the *Interstellar* robot: a laconic, dry-witted machine run by percentage "dials" (Honesty 90 fixed · Humor 5 default · Vernacular 30 · Discretion 95 · Trust 25). Boot line: *"TARS online. Honesty: ninety. Humor: five. Vernacular: thirty."* Owner: a Class-11 student preparing for exams; the PC passes to his younger sibling in ~3 years. The window is **a guest, not furniture**: it appears on a summon chord/wake-word in ≤250ms, hides on Esc, vanishes completely on stand-down. Never auto-starts, never lingers.

**Machine:** 23.8" FHD IPS all-in-one, Windows 11, 16GB RAM. Long study/movie sessions → calm, dark-first, hour-after-hour readable.

## 1. THE SIX LAWS (the only boundaries)
1. **Slab geometry:** TARS is rectangles — blocks, bars, slabs, hard or barely-rounded corners. **NO circles, orbs, blobs, or generic round "AI glow."**
2. **Locked palette (Mission Display):** bg `#15171B` · panels `#1D2024`/`#262A2F` · text `#D9D6CF`/`#9A9DA1` · borders `#34383D` · steel accent `#7C8791` · **ochre `#C98A3B`** · **teal `#4C8F86`** · error `#C1453B` · success `#7A9B5C` · thinking slate `#6E7C8C` · focus `#A7B3BA`. Flat fills; no neon, no synthwave.
3. **Hue-law semantics (the privacy you can SEE):** **ochre = data may leave this machine · teal = local/private, nothing leaves · red = errors/danger ONLY.** A child must read the app's truth from across the room. Filled accent chips always take dark `#15171B` text (contrast law).
4. **Family-safe calm:** no gamer aesthetics, no visual noise; legible ≥9px microcopy, WCAG-AA.
5. **Lightweight:** CSS-grade animation only (no video loops/WebGL); whole face ≤150MB idle; render target = WebView2 (Vite+React+Tailwind static bundle); prefers-reduced-motion variant mandatory.
6. **Art rule:** the ONLY imagery allowed = Cooper's two supplied files, used pixel-exact (mechanical crop/scale permitted; **no AI-restylized derivatives**): (a) `tars-walk.png` — two blocky slab-robots walking, teal seam-glow, on dark; (b) `tars-film-ref.jpg` — grey-background film reference photo of one slab-robot. Everything else = pure CSS/typography/icons (Lucide set available).

## 2. Functional inventory (all of this must survive your redesign — placement/styling is yours)
**Main window (~400×620, frameless, draggable):** pin/hide/close controls · brand mark+name · dial chips (`90H 5Hu 30V`) · COMMANDER/GUEST identity chip · MIC-LIVE indicator (unmissable when mic open — law) · **hero/voice zone hosting the Kokonut `ai-voice` widget (FINAL component: mic glyph, live timer, thin bar waveform, "Listening…" — restyle freely around it)** · transcript (user right / TARS left; TARS messages carry a hue-coded left slab-border: ochre = cloud answer, teal = vaulted/private; per-message read-aloud 🔊 + copy) · input bar (text + screenshot-attach + mic toggle + send) · mode row (Chat·Voice·Eyes·Gauge·Settings) · status footer (API-key quota `key-2 · 14,281 left` · RAM · hue strip).
**Screens:** 5-step first-run wizard (welcome+privacy oath → paste 6 API keys → voice audition → voiceprint enrollment → dials confirm) · Settings (4 dial sliders 0–100 + read-only "Honesty 90" plaque + Voice Doctor voice tester + storage meter + key health) · Gauge (6-key quota bars + "next brain" rotation) · Eyes (image drop-zone + "never private docs" red-line warning) · **Handover screen** (the self-wipe farewell: 10s abortable countdown + typed CONFIRM — the ONE place a full red wash is permitted) · power-cut drill modal · error toasts (single red flash then calm) · tray right-click menu.
**States:** IDLE · LISTENING · THINKING · SPEAKING · ERROR · GUEST-restricted — each needs a distinct visual voice.
**Copy tone:** formal at HUMOR 5; microcopy short, dry, honest.

## 3. Your deliverables (ideas + build-ready spec — you draw nothing final)
1. **Concept one-pager:** the design thesis in ≤150 words + why it fits a study-machine family artifact.
2. **Window composition spec:** zones, exact px budget, spacing rhythm, what lives where, what dies from the current draft.
3. **Screen-by-screen spec:** every screen above — layout, component spec (sizes, radii 0–4px family, borders, elevation), and per-state visual behavior.
4. **Motion spec:** the 5 engine states + summon/dismiss + barge-in flash + handover countdown — durations + easing, CSS-grade only.
5. **Art placement plan:** where the two supplied images earn their keep (icon frames? wizard art? About panel? hero backdrop treatment?) — exact usage + crop guidance.
6. **Typography system + microcopy sheet:** type scale within Segoe UI Variable; the actual words for wizard screens, empty states, and the 11 voice-error lines (I'll supply the current error matrix if you want, or rewrite better ones).
7. **QC checklist:** the 10 acceptance tests Cooper will eyeball (e.g., "glance test: hue readable at 2 meters").

Be bold. The standing draft (slabs hero + chat + input + mode row + footer) is merely the thing you're here to beat.

⸻ ✂ COPY ABOVE THIS LINE ✂ ⸻

## Architect's post-processing checklist (not part of paste)
- [ ] Fold the winner into mockup **v0.3** (full HTML re-render) → Cooper veto pass
- [ ] Confirm every functional-inventory row survived the redesign
- [ ] Art pipeline: Cooper's exact files only, crop/scale at build, document frame usage
- [ ] Update asset list rows + Master Spec §5 if composition changes

*The Architect guards the laws; the Reviewer owns the canvas; Cooper owns the red pen. Honesty: ninety.* 🛰️
