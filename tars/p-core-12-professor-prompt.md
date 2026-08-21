# P-CORE-12 — PROFESSOR + COUNCIL — THE FINAL CORE PHASE (operator prompt · Strict-Prompt Doctrine)
**Lane:** AGENT CORE only · **Jurisdiction:** `tars/core/` + ONE sanctioned append to `tars/agent-log.md` + ONE sanctioned doc bump: `tars/command-grammar.md` → **v1.7** (APPEND-ONLY; v1.0–v1.6 bytes untouched). `tars/app/` frozen. Nothing else.
**Base:** branch `main` at `d8f15f3` (P-CORE-11 tree, **651 checks green**, audit banked Aug 21). All 651 stay green and byte-stable except the §7-sanctioned re-aims.
**Date:** 2026-08-21 · suite chain …→445→495→540→595→651. **This is the last CORE phase — after audit: M-1 on the AiO.**

---

## 0. Read order (never skip)
1. `tars/tars-definition.md` v1.2 — **§24 Professor** (read PDFs aloud/explain **page-pinned** · quiz generation · spaced-repetition flashcards · Class-11 → JEE-grade rigor, PhD-horizon register · **Ultra lane: summoned only when NAMED**) · **§23 Council** (two or three lane models answer in parallel on SEPARATE ring keys → present both answers + TARS's own verdict on which to trust and why · *a special weapon, not a habit* — it costs 2–3× quota, so it stays a named request) · §31 privacy ladder · 7 Laws.
2. `tars/roadmap.md` P-CORE-12 row — acceptance: **quota arithmetic selftest (council = 2–3× flagged)**.
3. `tars/bridge-contract.md` v1.4 — quick_action `'council'` is rostered (line 48) and currently catch-alled; this phase earns it. Channels otherwise CLOSED; bus stays exactly 9.
4. Standing tree: `router.py` (LANE_MODELS, gates, lanes fast/smart/eyes/ears/ultra/council) · `keys.py` (LANE_CAPS, ledger) · `mouth.py` (speech ladder + privacy routing) · `findfile.py` (PDF location reuse) · `vault.py` (migrations) · `canon.py` · `selftest.py` (FixtureAdapter scripting).

## 1. What P-CORE-12 builds
**The desk becomes a teacher, and the ring learns to argue with itself — honestly, on command, never by habit.**

- `tars/core/pdf.py` — NEW. The PDF seam:
  - `PdfReader` protocol: `open(path) -> {pages: int, page_text(n) -> str}`.
  - `StdPdfReader` — **pure-stdlib MINIMAL extractor** (zlib FlateDecode streams + `Tj`/`TJ` string operators; ~text-layer PDFs only). Honest refusal law: no text layer / unsupported encoding → `LINE_PDF_OPAQUE` ("That PDF won't give me its text. Scanned pages, likely — I won't pretend to read them."), never a guess. (M-era may import-guard pypdf by decree — NOT this phase.)
  - `FixturePdf` — scripted pages, the suite's library.
  - File location rides `findfile.py` (confident-single / honest-list), Never-List pre-scan stands. `LINE_PDF_ABSENT = "I can't find that PDF. Name it, or point me at the folder."`
- `tars/core/professor.py` — NEW. The teacher:
  - **Read-aloud / explain, PAGE-PINNED:** "read page 3 of physics.pdf" → ack `"Reading page three."` then the page text through the mouth ladder. **Privacy routing decree: PDF content is Cooper's study material — speech rides LOCAL tiers only; edge tier never sees file content** (canary-pinned, the FRAME/CLIP pattern). "explain page 3" → ONE smart-lane call with the page slice — page bytes travel ONLY in that one explain call (hue amber, honest), never in read-aloud.
  - **Quizzes:** "quiz me on X" → ONE smart-lane draft (questions + held answer key), questions asked one at a time, grading LOCAL (fixture-grade keyword overlap) + the honest caveat `"I grade by key words. Your teacher grades better."` — never fake rigor. One draft call per quiz, pinned; zero calls while answering/grading.
  - **Flashcards + spaced repetition:** vault migration `flashcards(id, front, back, box, due_epoch)`, **Leitner boxes 1–5** (declared; wrong → box 1, right → box +1, due = box interval days — declare the interval table in code). Rows: "make flashcards for X" → ONE smart draft → stored · "remember this as a flashcard: front / back" → LOCAL add, zero ring · "flashcards" → due cards one at a time with reveal/grade flow · empty-due honest line.
  - **Professor register:** study rows ride a declared `study_prompt` (Class-11 → JEE rigor, PhD-horizon mentorship — bytes declared in professor.py, build on the §12 honesty clauses; never fork persona.py).
- `tars/core/council.py` — NEW. Parliament, on command:
  - **Named-summon ONLY** (`"council on …"` rows + the rostered chip): route_one → 3 seats IN PARALLEL on SEPARATE ring keys (seat plan = the standing LANE_MODELS council map — declare it; fixture adapters script the seats) → reply presents EACH seat's answer (seat names honest) + **TARS's verdict**: which seat to trust and why (deterministic composition in sandbox — fixture verdict; the verdict's basis is declared: agreement count / lane strength, never a coin flip).
  - **QUOTA ARITHMETIC = THE ACCEPTANCE (roadmap):** ONE council turn ledgers EXACTLY 3 seat calls across 3 distinct keys, gauge totals reflect the 3-spend, the reply's flag line says so (council costs like three questions — §23's 2–3× honesty, generative + pinned). A solo smart question beside it ledgers exactly 1 — contrast-pinned.
  - **Ultra lane (§24):** NAMED summon ONLY ("use ultra for …" / "ask the giant about …") → ONE ultra call, amber, ledgers ultra lane; **router NEVER auto-selects ultra/council** — the standing gate (council→ultra→smart→fast) treats named phrases only; battery contrasts pinned: unnamed complexity → smart, named ultra → ultra.
  - Ring discipline: council seats parallel but bounded (3); a drained seat answers honestly in-place ("seat three couldn't make it") — the mock scripts one; verdict composition must handle 2-of-3 gracefully, pinned.
- `command.py` — v1.7 rows: pdf read/explain · quiz · flashcards add/review/due · council · ultra-named · **the study BOUNDARY RETIRES** (the last declared boundary — after this phase zero boundary remains; the gb battery re-aims to pin its OWN completion honestly: study utterances now reach professor.py, and the boundary harness asserts its shut list is empty) · `quick_action('council', {text})` SERVED (the §7 re-aim) — `{}`/empty text → near-miss honest question, zero ring.
- `canon.py` — extend, generative + literal-pinned: `LINE_PDF_ABSENT` · `LINE_PDF_OPAQUE` (above) · `LINE_QUIZ_CAVEAT = "I grade by key words. Your teacher grades better."` · `due_ack(n)` → `f"{number_words(n)} cards due."` · council verdict family (pin ≥3 literals: unanimous, 2-of-3 with seat-three-absent, disagreement verdict) · `LINE_FLASH_EMPTY = "No cards due. Learn something, then come back."`

## 2. Privacy + ring discipline (battery PROVES, never claims)
- Read-aloud: file bytes in ZERO adapter payloads (canary-swept); explain: exactly ONE smart call carrying the page slice.
- Quiz/flash drafts: exactly ONE smart call each; grading/replay/review: ZERO.
- Council: exactly 3 seat calls on 3 distinct keys per turn; ultra-named: exactly 1 ultra call; unnamed-heavy: smart (contrast trio pinned against the gauge).
- §31 audience law extends: study content isn't personal-memory, but file bytes follow file-law; guest sessions can study facts but never touch Cooper's files/flashcards (flashcard recall = personal surfaces → matrix extends, pinned).

## 3. Grammar v1.7 (append-only; 3 example utterances per row)
Rows: pdf-read · pdf-explain · quiz · flash-make · flash-add · flash-due · council · ultra-named. Closed Hinglish aliases declared (suggest `padhai shuru`, `quiz le lo` — adjust but CLOSED). Row-for-row exercised.

## 4. Crash, determinism, guards
- Crash child: flashcards table survives SIGKILL; council turn interrupted mid-burst ledgers no phantom seats (seat ledger is per-call, append-only).
- urlopen/subprocess patched-RAISE extended over the new modules.
- All 651 prior byte-stable except §7. Determinism ×2. Expect ≈700–720.

## 5. Agent-log (one append-only entry)
What shipped · StdPdfReader's honest envelope (what it can/can't parse) · Leitner table · council seat plan + verdict basis · machine-taught fixes in the open · acceptance CORRECTION for P-CORE-11: "PASS, banked by Architect audit Aug-21 atop d8f15f3 — 651/651 re-run twice, Part IX literals + sole-survivor + irreversibility grep re-verified, history-window leak closure independently confirmed, PERSONAL-CANARY-47 matrix swept."

## 6. Deliverable + REPORT block (§3.5 shape — mandatory)
Whole files · zero dead code · zero unused imports (seam patterns recognized) · zero >U+2100 glyphs in code AND docstrings · zero new deps · zero network.
Commit: `[CORE] P-CORE-12 — Professor + Council: pure-stdlib PDF seam page-pinned, quizzes + Leitner flashcards, named ultra/council lanes with verdict, quota arithmetic, grammar v1.7, <N>-check selftest`.
REPORT: FILES · 7-LAWS RECITAL · SELFTEST OUTPUT (fresh-clone tail, twice) · CONTRACT CHECK ('council' chip served, channels closed, bus at 9) · KNOWN LIMITS (StdPdfReader text-layer-only honesty; real PDFs + heavy ultras = AiO-era) · RE-AIMS · PUSHED (fresh-clone-verified green).

## 7. Sanctioned re-aims (the ONLY tolerated diffs; disclose in-code + REPORT)
1. The gb boundary battery RETIRES: study rows reach professor.py; the harness re-pins its own shut list as empty — the final boundary closes.
2. `quick_action('council')` leaves the unshipped catch-all set; remaining names re-pin byte-exact.
3. Nothing else moves. Any further diff = FAIL.

**Never List + 7 Laws bind. §23's sentence is the phase: a special weapon, not a habit — and §24's: the giant is summoned only when named. The machine's truth over green lights. Finish the core — then we go wake the AiO.**
