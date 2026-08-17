# 📨 CLAUDE BRIEF #1 — TARS Color Scheme (paste-ready)
**Aug 10, 2026 · How to use:** copy EVERYTHING between the ✂ lines → paste into Claude → paste Claude's full reply back to the Architect. Claude designs nothing final — it returns ideas + AI-generation prompts; the Architect converts to tokens and re-tints the mockup.

⸻ ✂ COPY BELOW THIS LINE ✂ ⸻

# PROJECT BRIEF: "TARS" — color scheme consultation (no final designs, ideas + generator prompts only)

## 1. What the project is
A privacy-first, voice-first **desktop AI assistant named TARS** (inspired by the *Interstellar* robot), being built for a Class-11 student in India on a tight budget; the machine becomes a **family/sibling hand-me-down in ~3 years**. Personality is canon-style: laconic, dry, formal-by-default, run by percentage "dials" (Honesty 90 fixed · Humor 5 default · Vernacular 30 · Discretion 95 · Trust 25). Error and status lines are short and calm.

## 2. The machine it lives on
HP 24-cr0023in All-in-One desktop — Ryzen 7 7730U, 16GB RAM, 512GB SSD, **23.8" FHD IPS display**, Windows 11, x86, no NPU, always wall-powered. Uses: schoolwork, long PDF/video sessions, movies, light gaming (Minecraft), coding. The UI must stay **calm and readable over hours**, and feel native beside Windows 11 — this is a study machine and a family PC, not a gaming battlestation.

## 3. The UI skeleton (FIXED — your palette must serve this, not fight it)
- **Motif: TARS = rectangular slabs.** Blocks, bars, vertical slabs, square-ish corners. **NO circles, orbs, blobs, or round "AI glow" clichés.**
- **TARS Home** = a ~400×620 popup window (web-tech: Vite+React+Tailwind static bundle in a WebView2 shell). Anatomy, top→bottom:
  1. **Title bar:** mini slab logo · dial chips (`90H·5Hu·30V`) · COMMANDER ✓ chip · pin/hide/close
  2. **Hero zone:** the voice visualization (below) + state label (LISTENING/THINKING/SPEAKING) + "MIC LIVE" indicator
  3. **Chat transcript:** user bubbles right; TARS messages left with a **slab-style colored left border**
  4. **Input bar:** text field + attach + mic + send
  5. **Mode row:** Chat · Voice · Eyes · Gauge · Settings
  6. **Footer:** API-key/quota status · RAM · privacy hue strip
- **Voice UI (FINAL, locked):** Kokonut UI's `ai-voice` — minimal recorder-style widget: small mic glyph, live timer, thin bar waveform, "Listening…" label, generous negative space.
- **Icon (lineage locked):** four brushed-steel vertical slabs of varying heights, on a dark tile, thin glowing gaps between slabs (square app icon; concepts already generated — may need re-tinting to the new palette).
- **Other screens:** 5-step first-run wizard · Settings with **4 slider dials + a read-only "Honesty 90" plaque** · Gauge panel (quota bars per key) · Eyes panel (image drop-zone + privacy warning strip) · error toasts · a **danger-red "Handover" screen** (10-second abortable self-wipe countdown).
- **Component diet:** shadcn-style parts (Kokonut UI, React Bits, Watermelon, Lucide icons). Animations CSS-grade only; whole window idles ≤150MB.

## 4. The one hard semantic law the palette must preserve
**Hue Law:** one accent = *"data may leave this machine"* (cloud active) · a second accent = *"nothing leaves — local/private (vaulted)"* · a red reserved **only** for errors/danger. A ten-year-old sibling must be able to glance and know. You choose the hues; the semantics are non-negotiable.

## 5. What was VETOED (don't resurrect it)
Previous palette: deep navy `#0B0F1A` + neon cyan `#22D3EE` + indigo `#6366F1` — judged **"too gaming / too coding-IDE."** No neon-gamer glow. No synthwave.

## 6. YOUR TASK — ideas and decision material only
**A. Schemes:** propose EITHER one strong unified scheme OR 2–3 variants, in these directions (pick the strongest mix):
   - **"Interstellar film"**: warm desaturated steel/greys, space-black, mission-display neutrals, restrained ochre/dust accents — the movie's engineering calm, not fan-poster saturation.
   - **"Traditional AI assistant"**: calm, neutral, understated, family-safe.
   Every scheme must include a **full design-token table** (hex + role) covering: app background · surface/panel · elevated surface · primary text · secondary text · borders/dividers · primary action · **CLOUD accent (hue-law)** · **LOCAL/PRIVATE accent (hue-law)** · error red · success · thinking/processing tint · selection/highlight · focus ring · disabled state.
**B. Per scheme:** 60-30-10 usage rule · dark-first stance (state if a light variant is warranted) · why it suits long study/movie sessions + a family hand-me-down · how the hue-law maps.
**C. Component application notes (one line each):** title bar · slab logo · dial chips · COMMANDER/GUEST chips · hero/voice area (Kokonut ai-voice) · TARS vs user bubbles (+ the amber/private left-border variant) · input bar · mode row · footer hue strip · wizard · settings sliders · gauge bars · error toasts · handover danger screen.
**D. Accessibility:** list the key text/background pairs with WCAG-AA contrast verdicts.
**E. AI-generation prompt pack:** with your FINAL chosen hexes embedded, write copy-paste prompts (image-model style) for: (i) the 4-slab **app icon** re-tinted to the scheme (square, legible at 32px) · (ii) **wizard welcome illustration** (original art inspired-by a blocky monolith robot — NOT a copyrighted reproduction) · (iii) **About/empty-state art** · (iv) **tray icon pair** (asleep vs armed). Plus a one-paragraph "prompt style guide" so every future asset stays on-brand.
**F. Verdict:** rank the schemes, recommend one, ≤5 bullets of tradeoffs. Tables over prose throughout.

⸻ ✂ COPY ABOVE THIS LINE ✂ ⸻

## Architect's post-processing checklist (not part of paste)
- [ ] Lock winning scheme → rewrite Master Spec §5 constraint 2 + asset-list Law 2 + A-04 row
- [ ] Re-tint `tars/brand/b01-window-mockup.html` → present v0.2 for veto
- [ ] Run icon re-tint via Claude's generation prompt → replace A-01 master if superior
- [ ] Verify contrast pairs land on the real mockup, not just on paper

*Filed by the Architect. The Reviewer gets ideas; Cooper gets choices. Honesty: ninety.* 🛰️
