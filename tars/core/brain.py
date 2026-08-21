"""The Living Brain (bible §25.5): a brain, not a cache.

Four doctrines rule this file, all battery-pinned:

THE TREE — tars-brain/ under the data root (vault's parent; nt truth:
C:\\TARS\\data\\tars-brain\\ on the AiO). Declared shelves, markdown/JSON,
human-readable forever: people/ · journal/ · lessons/ · knowledge/ ·
plans/ · inner/. No size cap — §29: the meter (watcher) shows, nothing
cages. Every write is atomic tmp-then-rename (the standing crash law: a
reopened brain holds the old bytes OR the new, never half).

THE DAY — the journal folds at STAND-DOWN (the standing close event with
reason "stand down"; the kill-switch close folds NOTHING — Law 5 keeps
the panic path instant, battery-proven with zero ring calls). The journal
records only what truly passed through the machine: asks (by who), memory
captures, the failure lines the day actually spoke. An empty day writes
no journal. Re-fold is byte-idempotent.

THE SLEEP PASS — consolidate() folds the day into files over the ring,
RING-BOUNDED by decree: at most TWO smart-lane calls per pass (call 1
distills the journal into FILE blocks; call 2 merges touched people
profiles) — the battery counts. Ring spent/absent -> honestly DEFERRED:
journaled, kv-marked, spoken NOWHERE (declared silence — Cooper is not
woken for bookkeeping), and never retried same-day (storm law). One pass
per day, marked in kv.

THE INNER LAW — inner/ is TARS's own page. Sovereignty: inner bytes NEVER
appear in any ring-request payload (the sweep battery hunts a canary
across every call), NEVER reach a non-Cooper audience (journal/inner asks
from family/guest earn the canon refusal, zero content bytes), NEVER
leave the machine (no send/export path exists here). The mouth obeys the
dials; the mind stays free.

The A3 explorer (list_brain / brain_text) is READ-ONLY and path-CONFINED:
every path resolves inside the brain root — "..", absolute paths, and
symlink escapes earn a clean refusal dict. The host filesystem is never
touched. Belt pin: the explorer provably writes nothing (tree bytes +
mtimes identical across calls).
"""
import os
import re
from datetime import datetime
from pathlib import Path

from tars.core import canon

BRAIN_DIRS = ("people", "journal", "lessons", "knowledge", "plans", "inner")
JOURNAL_ASK_CAP = 10      # honest listing cap: a marathon day says its first ten asks
PREVIEW_CAP = 500         # A3 leaf preview bytes cap, then a plain "..."
CONSOLIDATE_CALL_CAP = 2  # decree: at most two smart-lane calls per sleep pass

KV_LAST_PASS = "brain:last_consolidation"      # iso day already passed (storm law)
KV_DEFERRED = "brain:consolidation_deferred"   # "yes" when the last attempt honestly deferred

# The journal's "what went wrong" detector is DECLARED and closed: a failure is a tars
# line from the canon failure family the day actually spoke. Nothing else counts as wrong.
WRONG_LINES = (canon.LINE_ALL_SPENT, canon.LINE_CLOUD_FAIL, canon.LINE_TELE_FAILED)

_FILE_RE = re.compile(r"^FILE:[ \t]*(?P<target>\S+)[ \t]*$", re.MULTILINE)
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")

CONSOLIDATE_SYSTEM = (
    "You are the sleep-cycle organizer for TARS, a desktop companion. Distill the day's "
    "journal into Living Brain file updates. Reply with ONLY update blocks, each shaped "
    "exactly:\nFILE: <dir>/<slug>.md\nWHY: <one honest line>\n---\n<full file bytes>\n"
    "Allowed dirs: people, lessons, knowledge, plans, inner. Whole files only, lowercase "
    "slugs. If nothing deserves filing, reply with no blocks."
)
MERGE_SYSTEM = (
    "You are the people-profile merge pass for TARS. You receive existing profile bytes and "
    "new fragments from today. Reply with whole-file rewrites in the same FILE protocol "
    "(allowed dir: people), nothing else."
)


def _day_of(iso_ts: str) -> str:
    """Vault stamps are ISO; the day is the first ten bytes. Honest, timezone-true."""
    return str(iso_ts)[:10]


def _atomic_write(path: Path, text: str) -> None:
    """tmp-then-rename in the SAME directory — a crash holds old bytes or new, never half."""
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


class Brain:
    """One mind per machine: the tree, the journal, the sleep pass, the explorer."""

    def __init__(self, vault, router=None, bus=None, root=None, now_fn=None):
        self._vault = vault
        self._router = router
        self._root = Path(root) if root is not None else Path(vault.path).parent / "tars-brain"
        self._now = now_fn or datetime.now
        for shelf in BRAIN_DIRS:
            (self._root / shelf).mkdir(parents=True, exist_ok=True)
        if bus is not None:
            bus.subscribe(self._on_close)  # the sleep-cycle fold rides the standing close seam

    @property
    def root(self) -> Path:
        return self._root

    def _on_close(self, kind: str, detail) -> None:
        """Fold ONLY on natural sleep (§25.5: journal first, then the quiet organizer pass).
        The kill-switch close folds NOTHING — Law 5 keeps the panic path instant, no pass."""
        if kind == "close" and (detail or {}).get("reason") == "stand down":
            if self.fold_day() is not None:
                self.consolidate()

    # ---------- the daily journal ----------

    def fold_day(self, day: str = None):
        """Compose the day's honest record from vault rows -> journal/<day>.md (atomic).
        Returns the path, or None for an empty day (nothing passed = nothing recorded)."""
        day = day or self._now().date().isoformat()
        asks, learnings, wrongs, exchanges, chats_touched = [], [], [], 0, set()
        for chat in self._vault.chat_rows():
            for row in self._vault.messages_for(chat["id"]):
                if _day_of(row["ts"]) != day:
                    continue
                exchanges += 1
                chats_touched.add(chat["id"])
                if row["who"] == "tars":
                    if row["text"] in WRONG_LINES and row["text"] not in wrongs:
                        wrongs.append(row["text"])
                else:
                    asks.append((row["who"], row["text"]))
        for mem in self._vault.recall():
            if _day_of(mem["ts"]) == day:
                learnings.append((mem["kind"], mem["text"]))
        if exchanges == 0 and not learnings:
            return None  # an empty day keeps an honest silence
        lines = [f"# Journal — {day}", "", "## What happened",
                 f"- {exchanges} exchanges across {len(chats_touched)} chats."]
        lines += ["", "## What was asked"]
        if asks:
            lines += [f"- {who}: \"{text}\"" for who, text in asks[:JOURNAL_ASK_CAP]]
            if len(asks) > JOURNAL_ASK_CAP:
                lines.append(f"- ({len(asks) - JOURNAL_ASK_CAP} more, kept in the vault)")
        else:
            lines.append("- Nothing was asked today.")
        lines += ["", "## What was learned"]
        lines += ([f"- [{kind}] {text}" for kind, text in learnings]
                  if learnings else ["- Nothing new was filed today."])
        lines += ["", "## What went wrong"]
        lines += ([f"- {line}" for line in wrongs] if wrongs else ["- Nothing went wrong."])
        path = self._root / "journal" / f"{day}.md"
        # a re-fold re-composes the day but NEVER erases the pass's own marginalia
        if path.is_file():
            old = path.read_text(encoding="utf-8")
            mark = old.find("\n## Consolidation")
            if mark != -1:
                lines += ["", old[mark + 1:].rstrip("\n")]
        _atomic_write(path, "\n".join(lines) + "\n")
        return path

    # ---------- the sleep pass ----------

    def consolidate(self, day: str = None) -> dict:
        """journal folds -> profiles/lessons/knowledge update. Ring-bounded: <= 2 smart calls.
        Deferred is honest: journaled + kv-marked + silent, and never retried the same day."""
        day = day or self._now().date().isoformat()
        report = {"day": day, "status": "nothing", "calls": 0, "files": []}
        if self._vault.kv_get(KV_LAST_PASS) == day:
            report["status"] = "done"  # one pass per day — a storm never re-runs it
            return report
        journal_path = self._root / "journal" / f"{day}.md"
        if not journal_path.is_file():
            return report  # a day with no journal has nothing to fold
        journal = journal_path.read_text(encoding="utf-8")
        if self._router is None:
            return self._defer(day, journal_path, journal, report, "no ring on this build")
        report["status"] = "done"
        self._vault.kv_set(KV_LAST_PASS, day)  # set BEFORE the calls: even a mid-pass crash never storms
        self._vault.kv_set(KV_DEFERRED, "no")  # a healthy pass clears yesterday's honest deferral
        first = self._router.route_lane(journal, "smart", system_prompt=CONSOLIDATE_SYSTEM)
        if not first["ok"]:
            # a spent ring never reached an adapter: the conversation count stays truthful zero
            return self._defer(day, journal_path, journal, report, "the ring was spent")
        report["calls"] += 1  # calls counts COMPLETED conversations — never an all-spent refusal
        blocks = self._parse_blocks(first["text"])
        fragments = self._write_blocks(blocks, report)
        people_touched = [t for t, _why in fragments if t.startswith("people/")]
        if people_touched and report["calls"] < CONSOLIDATE_CALL_CAP:
            prior = "\n\n".join(
                f"=== {target} (existing bytes) ===\n"
                + (self._root / target).read_text(encoding="utf-8")
                for target in people_touched)
            second = self._router.route_lane(journal + "\n\n" + prior, "smart",
                                             system_prompt=MERGE_SYSTEM)
            if second["ok"]:
                report["calls"] += 1
                self._write_blocks(self._parse_blocks(second["text"]), report)
            else:
                self._note(day, journal_path, "- Profile merge deferred: the ring was spent.")
        self._note(day, journal_path,
                   f"- Consolidation pass: {report['calls']} call(s), "
                   f"{len(report['files'])} file(s) updated.")
        return report

    def _defer(self, day, journal_path, journal, report, why) -> dict:
        report["status"] = "deferred"
        self._vault.kv_set(KV_LAST_PASS, day)
        self._vault.kv_set(KV_DEFERRED, "yes")
        journal = journal.rstrip("\n")
        if "## Consolidation" not in journal:
            journal += "\n\n## Consolidation\n"
        self._note(day, journal_path, f"- Consolidation deferred ({why}).", text=journal)
        return report

    def _note(self, day, journal_path, line, text=None) -> None:
        body = text if text is not None else journal_path.read_text(encoding="utf-8").rstrip("\n")
        if "## Consolidation" not in body:
            body += "\n\n## Consolidation\n"
        _atomic_write(journal_path, body.rstrip("\n") + "\n" + line + "\n")

    def _parse_blocks(self, reply: str) -> list:
        """FILE protocol -> [(target, why, body)]. Confined targets only; the rest never land.
        Line-wise by declaration: optional leading WHY line, then the --- fence, then bytes."""
        blocks = []
        matches = list(_FILE_RE.finditer(reply or ""))
        for idx, match in enumerate(matches):
            chunk = reply[match.end():matches[idx + 1].start() if idx + 1 < len(matches) else len(reply)]
            lines = chunk.split("\n")
            if lines and not lines[0].strip():
                lines.pop(0)  # the single line-break after the FILE marker itself
            why = ""
            if lines and lines[0].startswith("WHY:"):
                why = lines.pop(0)[4:].strip()
            if lines and lines[0].strip() == "---":
                lines.pop(0)
            body = "\n".join(lines).strip("\n") + "\n"
            target = self._confine(match.group("target"))
            if target is not None:
                blocks.append((target, why, body))
        return blocks

    def _confine(self, target: str):
        """A block target must be <declared dir>/<slug path> — nothing else earns the disk."""
        if not target or target.startswith(("/", "\\")) or ".." in target.split("/"):
            return None
        parts = target.split("/")
        if len(parts) < 2 or parts[0] not in BRAIN_DIRS:
            return None
        if any(not _SLUG_RE.match(part) for part in parts[1:]):
            return None
        return "/".join(parts)

    def _write_blocks(self, blocks, report) -> list:
        fragments = []
        for target, why, body in blocks:
            path = self._root / target
            path.parent.mkdir(parents=True, exist_ok=True)
            _atomic_write(path, body)
            report["files"].append(target)
            fragments.append((target, body))
            if why and target.startswith(("knowledge/", "lessons/")):
                # tomorrow's recall rides the standing memory surface; inner WHY never does
                self._vault.remember(target.split("/", 1)[0], why)
        return fragments

    # ---------- the A3 explorer (read-only, path-confined) ----------

    def _resolve(self, path: str):
        """None on ANY escape: '..', absolute (posix or drive), or a symlink pointing out."""
        raw = str(path or "").strip().replace("\\", "/")
        if raw in ("", ".", "/"):
            return self._root
        if raw.startswith("/") or ":" in raw.split("/", 1)[0]:
            return None  # an absolute path never earns a look at the host
        rel = raw.strip("/")
        if ".." in rel.split("/"):
            return None
        candidate = self._root / rel
        try:
            real_root = os.path.realpath(str(self._root))
            real_candidate = os.path.realpath(str(candidate))
        except OSError:
            return None
        if real_candidate != real_root and not real_candidate.startswith(real_root + os.sep):
            return None
        return candidate

    def list_brain(self, path: str = ""):
        """-> [BrainNode] {path, kind, sizeKb, modifiedDay}; escape -> a clean refusal dict."""
        node = self._resolve(path)
        if node is None:
            return {"ok": False, "line": canon.LINE_BRAIN_REFUSAL}
        if not node.is_dir():
            return []  # a leaf has no children; an absent shelf lists honestly empty
        nodes = []
        for child in sorted(node.iterdir(), key=lambda p: (p.is_file(), p.name)):
            rel = child.relative_to(self._root).as_posix()
            if child.is_dir():
                nodes.append({"path": rel, "kind": "dir", "sizeKb": 0.0,
                              "modifiedDay": datetime.fromtimestamp(
                                  child.stat().st_mtime).date().isoformat()})
            else:
                nodes.append({"path": rel, "kind": "file",
                              "sizeKb": round(child.stat().st_size / 1024, 1),
                              "modifiedDay": datetime.fromtimestamp(
                                  child.stat().st_mtime).date().isoformat()})
        return nodes

    def brain_text(self, path: str):
        """-> the leaf's preview bytes (capped); kind-mismatch/absent/escape -> refusal dict."""
        node = self._resolve(path)
        if node is None:
            return {"ok": False, "line": canon.LINE_BRAIN_REFUSAL}
        if node.is_dir():
            return {"ok": False, "line": canon.LINE_BRAIN_DIR}
        if not node.is_file():
            return {"ok": False, "line": canon.LINE_BRAIN_ABSENT}
        text = node.read_text(encoding="utf-8", errors="replace")
        return text if len(text) <= PREVIEW_CAP else text[:PREVIEW_CAP] + "..."
