# 🏛️ TARS Home — Design Commission v1 (Claude Reviewer, received Aug 10 2026)
**CANONICAL — as awarded, with Architect's two mandated fixes flagged at the end.**
Thesis: **"Instrument, not app."** TARS Home = a mission-readout panel that happens to hold a conversation.

## Composition canon (400×620, frameless, 0px outer radius, NO shadows)
| Zone | px | Law |
|---|---|---|
| Status strip | 40 | Title bar + dial chips + identity chip MERGED into one instrument row · pin/hide/close = bare glyphs |
| Hero/voice band | 128 | Kokonut ai-voice as a fixed instrument band — never grows; state label left (11px tracked), MIC-LIVE right, 0.5px bottom hairline |
| Transcript | ~302 flex | user right / TARS left, 2px hue left-border · 🔊/copy on HOVER only |
| Input bar | 56 | single row, 4px field radius only |
| Mode row | 32 | underline-slab active state, NOT filled pills |
| Footer | 24 | quota · RAM · **2px hue strip at the literal bottom edge** |
Spacing: 12px outer / 8px element / 4px tight pairs · zones separated by hairline, never gap-and-shadow.

## State grammar (canon)
IDLE = full stillness, flat teal strip · LISTENING = live waveform + pulsing MIC-LIVE · THINKING = indeterminate slate line + dial chips dim 60% · SPEAKING = waveform mirrors output · ERROR = single red flash then revert · GUEST = outline chip + lock glyph over dials. **Glow is earned, never ambient.**

## Screens (canon)
Wizard IS the window (5 slab-tick steps; film-ref photo as bordered "specimen plaque" on step 1) · Settings = single column, hairline-separated, square 8×8 slider thumbs, dashed-border Honesty plaque · Gauge = 6 ochre quota bars + steel rotation chips · Eyes = dashed drop slab + permanent non-dismissible red-line strip · **Handover = the ONLY full red wash** (10 slab ticks, monospace countdown, typed CONFIRM, OUTLINE-STEEL ABORT) · power-cut modal = calm flat overlay · toasts = single-instance, bottom-anchored · tray menu = OS-native feel, walk-art header thumbnail.

## Motion (CSS-grade)
Summon 140ms ease-out (≤250ms law) · dismiss 100ms linear no-scale · MIC pulse 1200ms · THINKING 1400ms slide · SPEAKING 60ms steps amp-driven · barge-in 120ms hue pulse · ERROR 150/400ms · handover 10×1000ms flat ticks · hover 100ms · **reduced-motion = static color swaps, zero loops.**

## Art plan (Cooper's exact files, mechanical crop/scale only)
- `tars-film-ref.jpg` → wizard step 1, hard-edged bordered plaque
- `tars-walk.png` → tray-menu header thumbnail (left robot crop) + **About panel sole illustration**

## Typography & microcopy (adopted)
Segoe UI Variable · 400/600 only · 13px 600 tracked state labels · 14px body/1.5 · 11px meta · ≥10px micro.
Wizard: *"TARS. Built to answer, not to watch."* / *"Six keys, six brains. Paste what you have — TARS works with fewer."* / *"Say something. Anything."* / *"Five phrases. Then TARS knows your voice from anyone else's."* / *"Honesty stays at ninety. The rest is yours to set."*
Empty states: *"Nothing said yet."* / *"All six keys, untouched."* / *"Drop an image. TARS will look, not keep."*

## QC checklist (Cooper's 10 eyeball tests)
2m hue glance · ≤250ms summon · zero-trace vanish · dark-text-on-accent · idle stillness · reduced-motion integrity · ≤4px radius audit · ≤150MB idle weight · red wash on Handover ONLY · hand-me-down identity cleanliness.

---
## ⚖️ ARCHITECT'S MANDATED FIXES (the review step earning its seat)
1. **Error-line conflict — REJECTED:** Claude's line *"Local model isn't loaded."* There IS no local brain (RAM Charter decree). Replaced by matrix rows 13–14 (Master Spec §1.2): *"That brain didn't answer. Trying another key."* / *"All six keys are spent. Standing by until reset."* Claude's other unique lines (perm-denied, no-network, catch-all) ADOPTED as rows 12/15/16.
2. **Tray-menu "Handover" entry:** allowed as a *door* only — execution still requires the §7.1 triple-gate (verified voice + passphrase + typed CONFIRM). Menu item can open the screen; it can never fire it.

*Full text preserved in chat record · this file is the design constitution for Phase 3.5.* 🛰️
