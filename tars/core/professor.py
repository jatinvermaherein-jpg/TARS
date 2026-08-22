"""The Professor (bible §24, P-CORE-12) — read-aloud/explain page-pinned, honest quizzes,
Leitner flashcards; Class-11 -> JEE rigor, PhD-horizon register; Ultra never lives here
(§24's giant answers named summons at the ROUTER gate, never through study rows).

THE STUDY REGISTER — study rows ride STUDY_PROMPT: the §12 honesty clauses VERBATIM
(persona reuse, never a fork) plus the declared professor register. Ring-needing rows
name it as the system prompt; read-aloud and reviews ride zero ring law.

RING DISCIPLINE (battery-pinned, never claimed):
- read-aloud: ZERO adapter calls; the page text mints LOCAL and queues one speak
  request — the standing mouth drain already speaks every queued item private=True,
  so the edge tier never sees file bytes (canary-pinned here at professor scale).
- explain: EXACTLY ONE smart-lane call; the page slice travels ONLY in that payload.
- quiz: exactly ONE smart draft; answering/grading is LOCAL keyword overlap +
  LINE_QUIZ_CAVEAT (never fake rigor); zero calls while answering.
- make flashcards: exactly ONE smart draft over the F:/B: protocol, then filed local.
- remember-this-as-a-flashcard: LOCAL, zero ring, bytes original-case (§17).

LEITNER (declared): boxes 1..5, LEITNER_DAYS below; a fresh card sits box 1 due NOW;
right climbs one box (cap 5); wrong returns to box one; due = grade-moment + days.

QUIZ/REVIEW STATE rides vault kv (crash-safe by the vault's own law): quiz:active JSON
+ flash:review pointer. A killed quiz mid-flight leaves the kv committed; rows consult
the pointer, never memory.
"""
import json

from tars.core import canon, persona

STUDY_PROMPT = (
    persona.HONESTY_CLAUSES
    + "\n\nYou are TARS in the Professor register: a physics mentor at Class-11 to JEE-grade "
      "rigor with a PhD horizon — precise, patient, derivation-first, never hand-wavy. "
      "When a page slice rides the question, teach FROM it; when drafting drills, keep the "
      "declared line protocol exactly so the desk can parse you."
)
QUIZ_QUESTIONS = 3        # one draft makes this many; one-at-a-time review
GRADE_OVERLAP = 0.5       # declared local grading bar: share of key words present
LEITNER_DAYS = (1, 2, 4, 7, 15)  # box 1..5 -> interval in days; declared table (battery-pinned)
QUIZ_KEY = "quiz:active"  # kv: {"topic", "questions": [{"q", "key"}], "i", "right"}
REVIEW_KEY = "flash:review"  # kv: {"id", "state": "front"|"back"}


def parse_qa_protocol(text: str, front_tag: str, back_tag: str) -> list:
    """The declared draft protocol: one `TAG: ...` pair per item, in order. Anything
    unpaired is ignored honestly — a partial draft files what parses, never invents."""
    items = []
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.upper().startswith(front_tag):
            if current is not None and current[1]:
                items.append(current)
            current = [line[len(front_tag):].strip(), ""]
        elif line.upper().startswith(back_tag) and current is not None:
            current[1] = line[len(back_tag):].strip()
    if current is not None and current[1]:
        items.append(current)
    return [(front, back) for front, back in items if front and back]


def grade_answer(answer: str, key: str) -> bool:
    """LOCAL grading, declared and pinned: share the key's words (>=4 chars, stop-free)
    present in the answer; GRADE_OVERLAP is the bar. The caveat line rides the summary."""
    stop = {"the", "and", "that", "this", "with", "from", "into", "your", "their", "then"}
    key_words = {w for w in "".join(c if c.isalnum() else " " for c in key.lower()).split()
                 if len(w) >= 4 and w not in stop}
    if not key_words:
        return False
    said = set("".join(c if c.isalnum() else " " for c in answer.lower()).split())
    return len(key_words & said) / len(key_words) >= GRADE_OVERLAP


class Professor:
    """The teacher engine: rows call these; every ring-needing path counts its calls."""

    def __init__(self, vault, router, pdf, finder, log, time_fn=None):
        import time as _time
        self._vault = vault
        self._router = router  # None stands: ring-needing rows answer LINE_STUDY_RING
        self._pdf = pdf
        self._finder = finder
        self._log = log
        self._time = time_fn or _time.time

    # ---------- the pdf rows ----------
    def _book_for(self, name: str):
        """finder law first (confident single / honest list / none), then the reader."""
        kind, found = self._finder.find(name)
        if kind == "none":
            return None, (canon.LINE_PDF_ABSENT, "local", None)
        if kind == "list":
            listing = "\n".join(f"{i + 1}. {path}" for i, path in enumerate(found))
            return None, (f"More than one match. Which one?\n{listing}", "local", None)
        return found, None

    def _page_of(self, book, name: str, page: int):
        """Page-pinning law: the book's real reach answers, never a guessed page."""
        if isinstance(book, str):  # a resolved path — open it now
            try:
                book = self._pdf.open(book)
            except Exception as exc:  # PdfOpaque, parser edge — honest refusal family
                self._log.entry("pdf", note=f"opaque: {exc}")
                return None, None, (canon.LINE_PDF_OPAQUE, "local", None)
        if not 1 <= page <= book.pages:
            return None, None, (canon.pdf_range_line(book.pages), "local", None)
        text = book.page_text(page)
        if not text.strip():
            return None, None, (canon.LINE_PDF_BLANK, "local", None)
        return book, text, None

    def read_page(self, name: str, page: int) -> dict:
        """Row (32): ack -> page text minted LOCAL -> ONE speak request for the page message.
        Zero adapter calls; the file's bytes never leave the box through this row."""
        found, refusal = self._book_for(name)
        if refusal:
            return {"lines": [refusal], "speak": None}
        book, text, refusal = self._page_of(found, name, page)
        if refusal:
            return {"lines": [refusal], "speak": None}
        return {"lines": [(canon.read_ack(page), "local", None), (text, "local", None)],
                "speak": 1}  # the page-text reply index — dialog queues its voice

    def explain_page(self, name: str, page: int) -> dict:
        """Row (33): EXACTLY ONE smart call; the page slice rides ONLY this payload,
        under the study prompt (§12 clauses aboard per the every-call law)."""
        found, refusal = self._book_for(name)
        if refusal:
            return {"lines": [refusal], "speak": None}
        if self._router is None:
            return {"lines": [(canon.LINE_STUDY_RING, "local", None)], "speak": None}
        book, text, refusal = self._page_of(found, name, page)
        if refusal:
            return {"lines": [refusal], "speak": None}
        ask = (f"Explain page {page} of {name} to your student — JEE depth, derivation-first.\n\n"
               f"{text}")
        reply = self._router.route_lane(ask, "smart", system_prompt=STUDY_PROMPT)
        lines = [(notice, "cloud", None) for notice in reply["notices"]]
        lines.append(((canon.explain_ack(page) + "\n" + reply["text"]) if reply["ok"]
                      else reply["text"], "cloud", reply["lane"]))
        return {"lines": lines, "speak": None}

    # ---------- the quiz rows ----------
    def quiz_active(self) -> bool:
        return self._vault.kv_get(QUIZ_KEY) not in (None, "")

    def start_quiz(self, topic: str) -> dict:
        """Row (34): ONE smart draft over the Q:/A: protocol -> the session opens at
        question one. A draft that parses empty answers LINE_QUIZ_THIN — never fake questions."""
        if self._router is None:
            return {"lines": [(canon.LINE_STUDY_RING, "local", None)], "speak": None}
        ask = (f"Draft a {QUIZ_QUESTIONS}-question quiz on {topic} for a JEE-track student. "
               "One question per line as 'Q: ...', each followed by its key as 'A: ...' "
               "(the key is held, never shown early). No other words.")
        reply = self._router.route_lane(ask, "smart", system_prompt=STUDY_PROMPT)
        lines = [(notice, "cloud", None) for notice in reply["notices"]]
        pairs = parse_qa_protocol(reply["text"], "Q:", "A:") if reply["ok"] else []
        if not reply["ok"] or not pairs:
            lines.append((canon.LINE_QUIZ_THIN if reply["ok"] else reply["text"], "cloud",
                          reply["lane"]))
            return {"lines": lines, "speak": None}
        session = {"topic": topic, "questions": [{"q": q, "key": k} for q, k in pairs],
                   "i": 0, "right": 0}
        self._vault.kv_set(QUIZ_KEY, json.dumps(session))
        lines.append((canon.quiz_question_line(1, len(pairs), pairs[0][0]), "cloud", reply["lane"]))
        return {"lines": lines, "speak": None}

    def answer_quiz(self, t: str) -> list:
        """The intercept's work: grade LOCALLY (keyword overlap + the caveat rides the
        summary), ask the next, close honestly. Zero ring while answering."""
        session = json.loads(self._vault.kv_get(QUIZ_KEY))
        questions = session["questions"]
        key = questions[session["i"]]["key"]
        right = grade_answer(t, key)
        session["right"] += 1 if right else 0
        session["i"] += 1
        verdict = canon.LINE_QUIZ_RIGHT if right else canon.quiz_wrong_line(key)
        lines = [(verdict, "local", None)]
        if session["i"] >= len(questions):
            self._vault.kv_set(QUIZ_KEY, "")
            lines.append((canon.quiz_score_line(session["right"], len(questions)), "local", None))
        else:
            self._vault.kv_set(QUIZ_KEY, json.dumps(session))
            nxt = questions[session["i"]]
            lines.append((canon.quiz_question_line(session["i"] + 1, len(questions), nxt["q"]),
                          "local", None))
        return lines

    def stop_quiz(self) -> list:
        self._vault.kv_set(QUIZ_KEY, "")
        return [(canon.LINE_QUIZ_STOPPED, "local", None)]

    # ---------- the flashcard rows ----------
    def add_flashcard(self, front: str, back: str) -> list:
        """Row (36): LOCAL filing, bytes original-case from the row above; zero ring."""
        card_id = self._vault.flash_add(front, back, self._time())  # box 1, due now
        self._log.entry("flash", note=f"card {card_id} filed local")
        return [(canon.LINE_FLASH_ADDED, "local", None)]

    def make_flashcards(self, topic: str) -> dict:
        """Row (35): ONE smart draft over the F:/B: protocol -> filed box 1 due now."""
        if self._router is None:
            return {"lines": [(canon.LINE_STUDY_RING, "local", None)], "speak": None}
        ask = (f"Draft flashcards on {topic} for a JEE-track student, 3 to 5 cards. "
               "One front per line as 'F: ...', each followed by its back as 'B: ...'. "
               "No other words.")
        reply = self._router.route_lane(ask, "smart", system_prompt=STUDY_PROMPT)
        lines = [(notice, "cloud", None) for notice in reply["notices"]]
        pairs = parse_qa_protocol(reply["text"], "F:", "B:") if reply["ok"] else []
        if not reply["ok"] or not pairs:
            lines.append((canon.LINE_QUIZ_THIN if reply["ok"] else reply["text"], "cloud",
                          reply["lane"]))
            return {"lines": lines, "speak": None}
        now = self._time()
        for front, back in pairs:
            self._vault.flash_add(front, back, now)
        lines.append((canon.flash_made_line(len(pairs)), "cloud", reply["lane"]))
        return {"lines": lines, "speak": None}

    def review_active(self) -> bool:
        return self._vault.kv_get(REVIEW_KEY) not in (None, "")

    def review_turn(self, t: str):
        """The armed-review intercept: the reveal word works while the front shows,
        right/wrong while the back shows; anything else is conversation and the desk
        stays armed (the pointer outlives the detour). Returns None when not consumed."""
        state = json.loads(self._vault.kv_get(REVIEW_KEY))  # armed by law: whole JSON (kv commits atomically)
        if state.get("state") == "front" and t == "reveal":
            return self.review_reveal()
        if state.get("state") == "back" and t in ("right", "wrong"):
            return self.review_grade(t == "right")
        return None

    def start_review(self) -> list:
        """Row (37): the due desk, one card at a time — front first, reveal by word."""
        due = self._vault.flash_due(self._time())
        if not due:
            return [(canon.LINE_FLASH_EMPTY, "local", None)]
        card = due[0]
        self._vault.kv_set(REVIEW_KEY, json.dumps({"id": card["id"], "state": "front"}))
        return [(canon.due_ack(len(due)), "local", None),
                (canon.flash_front_line(1, len(due), card["front"]), "local", None)]

    def review_reveal(self) -> list:
        state = json.loads(self._vault.kv_get(REVIEW_KEY))
        card = self._vault.flash_get(state["id"])  # exists by law: the pointer is set with the row
        self._vault.kv_set(REVIEW_KEY, json.dumps({"id": card["id"], "state": "back"}))
        return [(canon.flash_back_line(card["back"]), "local", None)]

    def review_grade(self, right: bool) -> list:
        """Leitner law: right climbs (cap box 5), wrong returns to box one; due re-stamped;
        then the next due card chains, or the desk-clear line. Zero ring throughout."""
        state = json.loads(self._vault.kv_get(REVIEW_KEY))
        card = self._vault.flash_get(state["id"])
        self._vault.kv_set(REVIEW_KEY, "")
        box = min(5, card["box"] + 1) if right else 1
        self._vault.flash_grade(card["id"], box, self._time() + LEITNER_DAYS[box - 1] * 86400.0)
        lines = [(canon.flash_grade_line(right, box), "local", None)]
        due = self._vault.flash_due(self._time())
        if not due:
            lines.append((canon.LINE_FLASH_DONE, "local", None))
        else:
            nxt = due[0]
            self._vault.kv_set(REVIEW_KEY, json.dumps({"id": nxt["id"], "state": "front"}))
            lines.append((canon.flash_front_line(1, len(due), nxt["front"]), "local", None))
        return lines
