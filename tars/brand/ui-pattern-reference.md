# UI PATTERN REFERENCE — what TARS adopts from public AI-agent UI kits
**v1.0 · Aug 17, 2026 · Ratified under the two art laws. This file is PATTERN guidance only — no third-party asset, style, font, color, or illustration enters the TARS bundle. Everything is redrawn in Mission Display tokens (`palette-mission-display.md`), Mission Display v2 soft-round geometry, system font stack, zero-emoji, Lucide-class inline SVGs hand-drawn.**

Source archetypes reviewed (Cooper-supplied links):
1. Figma Community — "AI Agent UI Kit" (free preview of a paid kit; teaser only)
2. Figma Community — "AI Chat UI Kit — free chatbot & agent interface templates" (CC BY 4.0, by Miki Mouse). Credit retained here per license.

## Adopted conventions (patterns, not assets)
1. **Message grouping** — Cooper's messages in quiet surface-2 bubbles; TARS flat-left with thin hue border. *(Already in the app.)*
2. **Streaming indication** — THINKING state as a subdued label + three CSS-dot pulse (glyph-free); SPEAKING shows the chunk stream. No spinners without meaning.
3. **Hover action bar** — copy · read-aloud · redo on TARS messages. *(Already in the app.)*
4. **Status chips** — state readable at a glance: small labelled dot + word (IDLE/LISTENING/THINKING/SPEAKING/ERROR), hue-honest. *(Already in the app.)*
5. **Empty-state composition** — large hero art (Cooper's walk-art) + one quiet line (the boot line). *(Spec'd; art lands at Merge.)*
6. **Prompt-input affordances** — attachments + push-to-talk in the composer; intent chips above it. *(Already in the app.)*
7. 🆕 **TOOL-CALL CARDS** — every Operator action renders in the transcript as a compact card: `intent → target → status` with status progressing `proposed → awaiting YES → done | cancelled`, hue-honest borders, glyph per intent (open/search/file/document/telesend/look/status). Confirm-gated cards obey the typed-YES modal (bridge-contract action events). **Assigned to P-APP-3.**
8. **Result cards** — search results and generated documents as tidy cards (title, source, open affordance), not raw text dumps. **Assigned to P-APP-3.**

## Explicitly rejected
- Kit colors, kit fonts (Inter), imported art/illustrations, light mode, heavy glassmorphism (backdrop-blur, glow, bloom). NOTE (Aug 17 v2): soft-round corners, soft shadows and the whisper sheen are no longer "kit style" — they became OUR canon via the skin ballot (bible §14 v2). Rejected is their assets and their look, not the geometry family.
- External fonts (Inter etc.) — system stack only; the bundle must run offline and sandboxed.
- Any imported art/illustration/icons — hand-drawn glyphs + Cooper's art, always.
- Light mode — not in scope (Mission Display is dark-only by lock).

## Discipline note for builders
Patterns describe *where things live and how they behave*, never *how they are colored or drawn*. If a kit shows a pattern that needs a new color, the pattern is adapted to the existing palette or dropped. When in doubt: palette wins, geometry wins, art laws win.
