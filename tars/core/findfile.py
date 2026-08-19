"""Natural-language find (command-grammar §5) — honest answers, never a guessed file.

Search space is DECLARED roots only (Desktop/Documents/Downloads on the AiO;
tmp-roots in the sandbox; TARS_FIND_ROOTS may extend on the host). Scoring is
declared and reviewable: name-token hits plus a recency bonus when the
description carries a hint ("from yesterday", "last week"). One confident
match answers with the path; several plausible rows earn the honest short
list (max 5) and a question; nothing plausible earns the declared none-line.
Ambiguity is never resolved by picking silently — §16.
"""
import os
from datetime import datetime

TOKEN_SCORE = 10        # per name-token hit
RECENCY_BONUS = 15      # mtime inside the hinted day-window
CONFIDENT_LEAD = 15     # top must lead second place by at least this much
MAX_LIST = 5
RECENCY_HINTS = (  # (phrase, day window size, anchor days back)
    ("today", 1, 0),
    ("yesterday", 1, 1),
    ("last week", 7, 7),
    ("this week", 7, 0),
    ("last month", 30, 30),
)
_STOP_WORDS = {"the", "a", "an", "from", "my", "of", "file", "find", "dhundo", "that", "me"}


def finder_roots_from_env():
    """Declared roots: env override first; AiO home folders on nt; empty elsewhere (honest)."""
    raw = os.environ.get("TARS_FIND_ROOTS", "").strip()
    if raw:
        return [p for p in raw.split(os.pathsep) if p]
    if os.name == "nt":
        home = os.path.expanduser("~")
        return [os.path.join(home, name) for name in ("Desktop", "Documents", "Downloads")]  # canon §16 folders
    return []  # canon: sandbox find space comes from test-injected tmp roots


class FileFinder:
    def __init__(self, roots: list, now=None):
        self._roots = list(roots)
        self._now = now or datetime.now  # clock injected so recency math is fixture-pinned

    def _tokens(self, description: str) -> list:
        words = [w.strip(".,?!'\"").lower() for w in description.split()]
        return [w for w in words if w and w not in _STOP_WORDS and len(w) > 1]

    def _window_days(self, description: str):
        lowered = description.lower()
        for phrase, span, back in RECENCY_HINTS:
            if phrase in lowered:
                return span, back
        return None

    def find(self, description: str):
        """-> ("single", path) | ("list", [paths]) | ("none", []). Deterministic, declared."""
        tokens = self._tokens(description)
        window = self._window_days(description)
        today = self._now().date()
        scored = []
        for root in self._roots:
            if not os.path.isdir(root):
                continue  # canon: a missing root is skipped honestly, never invented
            for dirpath, _dirs, files in os.walk(root):
                for name in files:
                    basename = name.lower()
                    score = sum(TOKEN_SCORE for token in tokens if token in basename)
                    path = os.path.join(dirpath, name)
                    if window is not None and score > 0:
                        age_days = (today - datetime.fromtimestamp(os.path.getmtime(path)).date()).days
                        span, back = window
                        if back <= age_days < back + span or (back == 0 and age_days == 0):
                            score += RECENCY_BONUS
                    if score > 0:
                        scored.append((score, os.path.getmtime(path), path))
        if not scored:
            return ("none", [])
        scored.sort(key=lambda row: (row[0], row[1], row[2]), reverse=True)
        # declared order: score desc, then newest first, then path desc for exact ties
        paths = [path for _score, _mt, path in scored]
        if len(scored) == 1 or scored[0][0] - scored[1][0] >= CONFIDENT_LEAD:
            return ("single", paths[0])
        return ("list", paths[:MAX_LIST])
