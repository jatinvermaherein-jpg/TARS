# 🎨 TARS Palette — LOCKED: "Mission Display v2"
**v1 ratified Aug 10, 2026 → v2 RATIFIED Aug 17, 2026** (Cooper decree "override Mission Display — modern and aesthetic," structured ballot = soft-round · soft-glass · amber+mint, then one-click **"v2 locked"**). The v1 slab-flat scheme is RETIRED to the museum (bottom of this file) alongside parked Scheme B "Traditional Calm." Ratified visual reference: `mission-display-v2-preview.html` — the exact render Cooper locked.

## Design law intent
Interstellar-console calm, modernized: a deeper neutral ramp, soft-round corners, restrained glass depth, warm signal hues. Dark-first (study/movie machine; IPS bleed + eye strain). **No glow, no bloom, no neon, no colored shadows.** Red exists ONLY as alarm. Art laws sovereign: Cooper's supplied images only, zero emoji, system font stack.

## The v2 tokens (the law — 15 hexes + 2 on-accent)
| Token | Hex | Role |
|---|---|---|
| Background | `#0F1115` | window base |
| Surface-1 | `#171B22` | cards, transcript zone |
| Surface-2 | `#1F2530` | elevated cards, user bubble, inputs |
| Surface-3 | `#262E3B` | raised layer (status chips, hover fills) |
| Hairline | `#262C38` | borders everywhere |
| Text | `#ECECEF` | body |
| Text-dim | `#9CA3AF` | timestamps, labels |
| Text-faint | `#6B7280` | placeholders, tertiary |
| Steel | `#8A94A3` | neutral actions, glyph strokes |
| **🔶 CLOUD = warm amber `#F2AD4E`** | "data may leave this machine" |
| **🟩 LOCAL = mint `#5CD6AE`** | "vaulted — nothing leaves" |
| Error | `#E0655C` | errors + Handover screen ONLY |
| Success | `#7FBB6B` | confirmations (glyph-paired, never bare color) |
| Thinking | `#8195AB` | THINKING pulse |
| Focus ring | `#AAB6C4` | keyboard focus |
| On-accent (contrast law) | `#0B0E12` on mint · `#191207` on amber | filled accents NEVER take white text |

## Geometry (soft-round)
`8px` buttons/inputs/small chips · `12px` cards · `16px` panels/modals/sheets · `999px` capsules (state pill, hue pill, lane tag, jump pill, keyboard chips) · message bubbles asymmetric `16px 16px 8px 16px` · glyph tiles 9–10px · window shell 18px. **TARS answers stay flat-left with the 2px hue border — TARS does not bubble.**

## Depth (soft-glass, restrained)
- Raised (cards, bubbles, input bar, jump pill): `0 4px 14px rgba(0,0,0,.28)`
- Floating (YES modal, popovers, dropdowns): `0 10px 28px rgba(0,0,0,.38)`
- Sheen: header strip, input strip, raised cards get `linear-gradient(180deg, rgba(255,255,255,.035), rgba(255,255,255,0))`. Transcript body stays matte.

## Derived alpha utilities (the ONLY non-hex colors allowed)
Selection = mint 14% alpha fill + 1px mint border · disabled **control** = surface-2 at 45% alpha fill behind text-faint · status chips may tint their lane hue ≤16% alpha · hairlines may soften to white ≤10% alpha · **modal scrim** = background at ~82% alpha. Nothing else. No other hexes, ever. *(Scrim + disabled-control added Aug 18 — spec gap found and honestly flagged by Lane A's P-APP-2.5 fix report.)*

## Hue-law components (semantics UNCHANGED from v1 — only the hexes moved)
Waveform bars steel→amber/mint · TARS reply left-border hue · footer hue strip · mic glyph hue · header pill · Cooper-ID chip (filled steel, dark text; GUEST outline-only) · dial chips/sliders neutral steel (dials are information, not hue-law) · gauge warn = lane hue at ≤20% remaining (inclusive).

**60-30-10** still governs usage. **One exception stands:** the Handover screen is allowed a full error-tinted wash (it must FEEL different).

## Retired — museum (banned in product; audit greps against these)
v1 hexes: `#15171B` `#1D2024` `#262A2F` `#D9D6CF` `#9A9DA1` `#34383D` `#7C8791` `#C98A3B` `#4C8F86` `#C1453B` `#7A9B5C` `#6E7C8C` `#A7B3BA` — plus names "ochre"/"teal" as canon words. 0px slab corners and the flat/no-shadow rule retired with them. The old AI-asset prompt pack is RETIRED — the art law (Cooper's supplied art only) supersedes it; nothing AI-generated enters the bundle. Scheme B "Traditional Calm" stays parked, museum-grade.

## Changelog
- v1 → LOCKED Aug 10, 2026 (replaced vetoed navy/cyan "gaming-IDE" scheme)
- **v2 → LOCKED Aug 17, 2026** (ballot: soft-round / soft-glass / amber+mint — "v2 locked" ratification; same-day surgical canon wave: bible v1.2 §13–§14, contract A4 v1.4, this file)
- v2.0.1 → Aug 18, 2026: scrim (background ~82% alpha) + disabled-control (surface-2 45% alpha) utilities canonized after Lane A's honest flag; compact `rgba(...)` byte formatting is the bundle-wide audit norm

*Steel and two signal hues. A ten-year-old can learn it in one glance; a physicist can live in it for years.* 🛰️
