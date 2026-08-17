# 🎨 TARS Palette — LOCKED: Scheme A "Mission Display"
**Decided Aug 10, 2026 · Route: Claude Reviewer consult → Architect implementation · Scheme B "Traditional Calm" parked below as a drop-in re-skin (same structure, warmer neutrals, gold/sage accents) if A ever reads "too console" on the family machine.**

## Design law intent
Interstellar-console calm: desaturated steel neutrals, flat fills, barely-rounded corners, **no gradients-as-glow, no orbs.** Dark-first (study/movie machine; IPS bleed + eye strain). Red exists ONLY as alarm.

## The tokens (the law)
| Token | Hex | Role |
|---|---|---|
| Background | `#15171B` | window base |
| Surface | `#1D2024` | cards, transcript, mode row |
| Elevated | `#262A2F` | popovers, modals, user bubble |
| Primary text | `#D9D6CF` | body, transcript |
| Secondary text | `#9A9DA1` | timestamps, labels, footer |
| Borders | `#34383D` | hairlines, slab edges |
| **Primary action** | `#7C8791` | buttons, active icon steel |
| **🔶 CLOUD = ochre `#C98A3B`** | "data may leave this machine" |
| **🟩 LOCAL = teal `#4C8F86`** | "vaulted — nothing leaves" |
| Error/danger | `#C1453B` | errors + Handover screen ONLY |
| Success | `#7A9B5C` | confirmations (glyph-paired, never bare color) |
| Thinking | `#6E7C8C` | THINKING pulse |
| Selection | `#2B3A3E` fill + `#4C8F86` border | — |
| Focus ring | `#A7B3BA` | keyboard focus |
| Disabled | `#52565C` on 50% fill | — |

**60-30-10:** 60 neutrals · 30 elevated/borders/text · 10 accents — accents live as 1–2px slab borders, icons, state pulses; **one exception: the Handover screen is allowed a full `#C1453B`-tinted wash** (it must FEEL different).
**Contrast law:** filled accent chips/buttons take **`#15171B` dark text, NEVER white** (white fails AA on ochre/teal).

## Hue-law in the components (the teaching moments)
- **Waveform bars (Kokonut ai-voice):** steel at rest → **ochre mid-cloud reply** → **teal mid-local processing.** The single biggest lesson in the UI.
- **TARS bubble left-slabs:** default `#34383D` · cloud answer → **ochre** · vaulted/private → **teal**. User bubbles: no accent — signal is TARS-only.
- **Footer hue strip:** teal idle → ochre while any cloud call in flight → red flash on error. The sibling glance-test.
- **Mic glyph:** ochre while recording→cloud, teal while recording→local.
- **COMMANDER chip:** filled `#7C8791`, dark text · GUEST: outline-only.
- **Dial chips + slider fills:** neutral steel — dials are information, not hue-law.

## AI-generation prompt pack (hexes embedded — copy-paste grade)
**Style guide for ALL future assets:** *flat, matte, engineering-console; hard corners; no glass/glow/bloom/lens flare; subtle metal-brush only on steel; palette strictly {#15171B, #1D2024, #262A2F, #7C8791, #C98A3B, #4C8F86, #C1453B, #D9D6CF}; rectangular/slab geometry only, no circles; single soft top-down light.*

1. **App icon:** *Square 512px flat icon: four vertical brushed-steel slabs of varying heights side by side on `#15171B`, thin glowing gaps in teal `#4C8F86`; matte, no bevel gloss; legible as four distinct bars at 32px; no circles, no text.*
2. **Wizard welcome:** *Original minimalist illustration of a blocky monolithic slab-built robot standing centered on flat `#15171B`, one teal `#4C8F86` seam-line; engineering-diagram calm, wide negative space; purely geometric original design.*
3. **About/empty state:** *Flat vector empty mission panel: faint rectangular slab outlines `#34383D` on `#15171B`, one small ochre `#C98A3B` dot off-center; extremely sparse.*
4. **Tray pair:** *32px, same 4-slab mark — asleep: slabs `#262A2F`, gaps unlit; armed: gaps lit teal `#4C8F86` (ochre `#C98A3B` variant reserved to depict active-cloud state).*

## Changelog
- v1 → LOCKED Aug 10 2026 (replaces vetoed navy/cyan "gaming-IDE" scheme)

*Steel and two signal hues. A ten-year-old can learn it in one glance; a physicist can live in it for years.* 🛰️
