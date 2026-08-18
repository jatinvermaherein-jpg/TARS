# AGENT APP — FINAL ARCHIVE (lane frozen for P3 Merge Day)

**Frozen commit:** `ba36bc2` — `[APP] P-APP-3 operator surfaces: tool-call cards, result/file cards, TeleSend stage, LOOK band, chords`
**Architect verdict:** P-APP-3 = PASS, banked. APP lane FROZEN FOR MERGE (`9402ee0`).
**Verified:** working tree clean; upstream `9402ee0` touched only `tars/build-log.md` + `tars/roadmap.md` — zero APP files. Freeze is intact.

---

## §3.5 REPORT — FINAL (P-APP-3, as frozen)

### FILES (line counts read back from commit `ba36bc2`)

| File | Lines | Contents |
|---|---:|---|
| `tars/app/index.html` | 219 | 16 sprite symbols (`ic-search` added); sidebar quick actions incl. `open`/`search`/`whatsapp`; `#look-band` WATCHING band docked between `<header>` and `.transcript`; one YES modal. |
| `tars/app/app.css` | 843 | Operator cards (`.op-card` + status/glyph states), result & file cards (`.res-card`), TeleSend stage (`.stage-*`), LOOK band (`.look-band`, `.lb-*`), About chords (`.chord-row`). §8 carry-over debt paid. |
| `tars/app/app.js` | 1357 | Card lifecycle renderer, result/file/stage/WhatsApp cards, LOOK session engine, Enter-submit on the gate, three chords in About, `addReplyLine`. |
| `tars/app/mock.js` | 627 | Operator arc: open → search (3 rows) → open-the-second → document → telesend gate → WhatsApp text-link → look/enough. |

> Correction to my couriered report: I stated `app.js` 1409 L and `mock.js` 621 L. The frozen commit holds **1357 L** and **627 L**. The earlier figures were read from a mid-edit buffer, not the commit. Everything else in that report verified true.

### SELFTEST OUTPUT

`SCENES/CHECKS: 215 passed, 0 failed` — 166 prior + **49 new P-APP-3 checks**.
Reproduced after this session's snapshot restore from a **clean-room rebuild** (fresh `/tmp/h`, fresh puppeteer, reinstalled Chrome libs) against the frozen tree: **215/0 again**.
Full log: `selftest-output.txt`. Harness: `selftest.js`, shot scripts `shot-p1.js` · `shot-p2.js` · `shot-p25.js` · `shot-p3.js`.

### CONTRACT CHECK

- Method surface unchanged — harness asserts exactly the 10 contract names.
- **No new event channels.** Cards drive off existing `action` + `confirm` + `done`.
- Every dispatched `quick_action` name asserted inside the contract-listed set (check #211-series).
- Skin law: zero new hexes · zero retired v1 bytes · all rgba byte-compact · new radii on the soft-round scale.
- One YES modal only. Statuses limited to `proposed` / `awaiting YES` / `done` / `cancelled`.

**Frozen-tree forbidden-surface sweep (re-run at archive time):** emoji `0` · retired v1 hexes `0` · external asset refs `0` · spaced rgba literals `0`.

### KNOWN LIMITS (carried into merge)

1. Green cards render only for app-dispatched `quick_action` intents (`dispatch_only` ruling). Typed `"open Chrome"` produces no card — asserted, not accidental.
2. **Open question for merge:** the phase prompt's lo-fi search arc collided with banked canon `"Opening result two. Ashish Chanchlani, interview clip."` I kept **both** rather than overwrite canon — typed *Ashish* queries keep the banked line; the lo-fi query drives the card arc. If one should be retired, that is a CORE/Architect call at merge.
3. Frame counter and `sent (demo)` are demo-side. Nothing is sent, launched, or captured.
4. Harness lives outside the bundle. Shipped bundle remains **5 files, zero deps, zero build**.

---

## Screenshot sweep — full archive (`archive/`, 21 PNGs @ 2480×1560)

### P-APP-3 hard gate (9)
| File | What the pixels proved |
|---|---|
| `p3-green-card-done.png` | Dispatched green verb lands on `done`: mint status pill, steel border, **no** focus ring. |
| `p3-result-cards.png` | Three result rows with rank / title / source / `open` — cards, not a text dump. |
| `p3-telesend-stage.png` | Stage card `physics-notes.pdf → Bhaiya on Telegram` sits legibly *beneath* the modal, not replaced by it. |
| `p3-modal-open.png` | The one YES modal floats over the inline card; Confirm armed only by uppercase YES. |
| `p3-red-card-awaiting.png` | Amber `awaiting YES` pill + focus `#AAB6C4` border while the gate is open. |
| `p3-telesend-sent.png` | Post-YES: card `done`, `sent (demo)` note, and the confirmation line **no longer red**. |
| `p3-look-band.png` | Full-width WATCHING band flush under the header, amber accent, live `3 frames`, classifier line, `stop`. |
| `p3-whatsapp-link-card.png` | Text-link card notes the `wa.me` deep link; no gate, no staged file — file-send never rendered. |
| `p3-about-with-chords.png` | Three chords as plain monospace text, no art. |

### Prior phases banked (12)
`p1-streaming-midflight` · `p1-jump-pill` · `p2-panel-{dials,voice,keys,privacy,memory,system,about}` · `p2-honesty-refusal` · `p25-shell-empty` · `p25-yes-modal`

### The line that matters — what pixels proved that DOM checks could not

Every DOM assertion passed while `"Confirmed. a1 executing."` rendered with the **red error border**. `answerAction` routed *both* gate outcomes through `addErrorLine`, so a success was painted as a failure. String comparison saw the correct text and moved on; only the screenshot showed TARS lying about its own hue. Fixed via `addReplyLine`, with a permanent regression guard added. **This is the fifth time a text-only assertion missed a real rendering bug — screenshot and look.**

---

## Lane history — five phases, all PASS

| Phase | Commit | Result |
|---|---|---|
| P-APP-0 — Bridge shell + mock bridge | `4f1088f` | PASS |
| P-APP-1 — conversations wired | `38d1c8a` | PASS |
| P-APP-2 — Settings as a full app-page | `57dd85f` | PASS |
| P-APP-2.5 — Mission Display v2 reskin | `ce66d8d` → fix `030a1c7` | PASS |
| P-APP-3 — operator surfaces | **`ba36bc2`** | PASS — **FROZEN** |

## Merge-Day notes for whoever picks this up

- **Restore hazard (bit me twice):** snapshot restores wipe `/tmp`, strip `~/.ssh` perms, delete the `origin` remote, and remove Chrome's system libs. Recovery: `chmod 600 ~/.ssh/tars_app ~/.ssh/config` · re-add `origin` · rebuild `/tmp/h` from this mirror · `npm i puppeteer` · reinstall libs (**`libasound2t64`**, not `libasound2`).
- **Never force-push.** `git -c user.name="AGENT APP" -c user.email="app@tars.local" pull --rebase origin main` (name remote+branch explicitly), verify the upstream diff missed your lane, re-run the selftest, then push.
- Byte-exactness is audited literally — copy canon strings verbatim from `tars/brand/mission-display-v2-preview.html`.
