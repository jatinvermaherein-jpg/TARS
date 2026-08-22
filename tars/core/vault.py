"""vault.db — local SQLite personal memory (bible §30 ledger spirit).

WAL mode + synchronous=FULL: committed rows survive a SIGKILL / power cut, an
interrupted transaction rolls back cleanly, and integrity_check proves it on
re-open. `memory` and `ledger` are strictly append-only (INSERT only); `kv`
holds point-in-time state and therefore upserts — the crash-safety law is
about durability, which WAL gives both.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS kv (
    name  TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    date  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS memory (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    ts   TEXT NOT NULL,
    kind TEXT NOT NULL,
    text TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ledger (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    ts       TEXT NOT NULL,
    lane     TEXT NOT NULL,
    keyindex INTEGER NOT NULL,
    tokens   INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS chats (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    title    TEXT NOT NULL,
    created  TEXT NOT NULL,
    last_hue TEXT
);
CREATE TABLE IF NOT EXISTS messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id    INTEGER NOT NULL,
    who        TEXT NOT NULL,
    text       TEXT NOT NULL,
    ts         TEXT NOT NULL,
    hue        TEXT,
    lane       TEXT,
    superseded INTEGER
);
CREATE TABLE IF NOT EXISTS reminders (  -- P-CORE-6: durable clock workload, same WAL posture
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    text      TEXT NOT NULL,
    due_epoch REAL NOT NULL,
    repeat    TEXT NOT NULL DEFAULT '',
    kind      TEXT NOT NULL DEFAULT 'reminder',
    done      INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS timers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    label      TEXT NOT NULL,
    ends_epoch REAL NOT NULL,
    done       INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS contacts (  -- P-CORE-7 people-book: name is the case-insensitive key, display kept
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL,
    telegram TEXT NOT NULL DEFAULT '',
    whatsapp TEXT NOT NULL DEFAULT '',
    added_on TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sent_log (  -- P-CORE-7: append-only journal of what LEFT the box (success only, never intent)
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    channel    TEXT NOT NULL,
    recipient  TEXT NOT NULL,
    kind       TEXT NOT NULL,
    summary    TEXT NOT NULL,
    sent_epoch REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS flashcards (  -- P-CORE-12: the Leitner desk (bible §24), same WAL posture
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    front     TEXT NOT NULL,
    back      TEXT NOT NULL,
    box       INTEGER NOT NULL DEFAULT 1,
    due_epoch REAL NOT NULL
);
"""


def _now() -> str:
    return datetime.now().isoformat(timespec="milliseconds")


class Vault:
    """Crash-safe local store: kv state, journal memory, quota ledger."""

    def __init__(self, path: Path):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # check_same_thread=False lets council-lane worker threads ledger under
        # the router's single writer lock; every write still commits+fsyncs.
        self._db = sqlite3.connect(str(self._path), check_same_thread=False)
        self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.executescript(_SCHEMA)
        self._db.commit()

    def kv_set(self, name: str, value: str) -> None:
        self._db.execute(
            "INSERT INTO kv (name, value, date) VALUES (?, ?, ?) "
            "ON CONFLICT(name) DO UPDATE SET value = excluded.value, date = excluded.date",
            (name, str(value), _now()),
        )
        self._db.commit()

    def kv_get(self, name: str):
        row = self._db.execute("SELECT value FROM kv WHERE name = ?", (name,)).fetchone()
        return row[0] if row else None

    def kv_scan(self, prefix: str, only_value=None) -> list:
        """[(name, value)] rows under a literal prefix — the speak queue's intake view."""
        sql = "SELECT name, value FROM kv WHERE name LIKE ?"
        params = [prefix + "%"]
        if only_value is not None:
            sql += " AND value = ?"
            params.append(only_value)
        sql += " ORDER BY name"
        return [(name, value) for name, value in self._db.execute(sql, params).fetchall()]

    def remember(self, kind: str, text: str) -> int:
        cur = self._db.execute("INSERT INTO memory (ts, kind, text) VALUES (?, ?, ?)", (_now(), kind, text))
        self._db.commit()
        return int(cur.lastrowid)

    def recall(self, kind=None) -> list:
        if kind is None:
            rows = self._db.execute("SELECT ts, kind, text FROM memory ORDER BY id").fetchall()
        else:
            rows = self._db.execute("SELECT ts, kind, text FROM memory WHERE kind = ? ORDER BY id", (kind,)).fetchall()
        return [{"ts": ts, "kind": kd, "text": tx} for ts, kd, tx in rows]

    def memory_count(self) -> int:
        return int(self._db.execute("SELECT COUNT(*) FROM memory").fetchone()[0])

    def spend(self, lane: str, keyindex: int, tokens: int) -> int:
        cur = self._db.execute(
            "INSERT INTO ledger (ts, lane, keyindex, tokens) VALUES (?, ?, ?, ?)",
            (_now(), lane, int(keyindex), int(tokens)),
        )
        self._db.commit()
        return int(cur.lastrowid)

    def ledger_total(self) -> int:
        return int(self._db.execute("SELECT COALESCE(SUM(tokens), 0) FROM ledger").fetchone()[0])

    def ledger_tail(self, limit: int = 5) -> list:
        """Newest ledger rows, chronological order (the gauge's audit trail)."""
        rows = self._db.execute(
            "SELECT ts, lane, keyindex, tokens FROM ledger ORDER BY id DESC LIMIT ?", (int(limit),)
        ).fetchall()
        return [{"ts": ts, "lane": lane, "keyindex": keyindex, "tokens": tokens}
                for ts, lane, keyindex, tokens in reversed(rows)]

    def chat_insert(self) -> int:
        """One row, written once. Title/last_hue are derived at read time — never edited."""
        cur = self._db.execute("INSERT INTO chats (title, created, last_hue) VALUES (?, ?, ?)", ("", _now(), None))
        self._db.commit()
        return int(cur.lastrowid)

    def chat_rows(self) -> list:
        rows = self._db.execute("SELECT id, created FROM chats ORDER BY id").fetchall()
        return [{"id": cid, "created": created} for cid, created in rows]

    def chat_first_user_text(self, chat_id: int):
        row = self._db.execute(
            "SELECT text FROM messages WHERE chat_id = ? AND who = 'cooper' AND superseded IS NULL ORDER BY id LIMIT 1",
            (int(chat_id),),
        ).fetchone()
        return row[0] if row else None

    def chat_last_hue(self, chat_id: int):
        row = self._db.execute(
            "SELECT hue FROM messages WHERE chat_id = ? AND hue IS NOT NULL AND superseded IS NULL "
            "ORDER BY id DESC LIMIT 1",
            (int(chat_id),),
        ).fetchone()
        return row[0] if row else None

    def message_add(self, chat_id: int, who: str, text: str, hue, lane) -> int:
        cur = self._db.execute(
            "INSERT INTO messages (chat_id, who, text, ts, hue, lane, superseded) VALUES (?, ?, ?, ?, ?, ?, NULL)",
            (int(chat_id), who, text, _now(), hue, lane),
        )
        self._db.commit()
        return int(cur.lastrowid)

    def message_get(self, message_id: int):
        row = self._db.execute(
            "SELECT id, chat_id, who, text, ts, hue, lane, superseded FROM messages WHERE id = ?",
            (int(message_id),),
        ).fetchone()
        return self._message_dict(row) if row else None

    def messages_for(self, chat_id: int, include_superseded: bool = False) -> list:
        sql = "SELECT id, chat_id, who, text, ts, hue, lane, superseded FROM messages WHERE chat_id = ?"
        if not include_superseded:
            sql += " AND superseded IS NULL"
        sql += " ORDER BY id"
        return [self._message_dict(row) for row in self._db.execute(sql, (int(chat_id),)).fetchall()]

    def message_context(self, chat_id: int, before_id: int, limit: int = 10) -> list:
        """Rolling window: the newest <=limit visible messages before before_id, chronological."""
        rows = self._db.execute(
            "SELECT id, chat_id, who, text, ts, hue, lane, superseded FROM messages "
            "WHERE chat_id = ? AND superseded IS NULL AND id < ? ORDER BY id DESC LIMIT ?",
            (int(chat_id), int(before_id), int(limit)),
        ).fetchall()
        return [self._message_dict(row) for row in reversed(rows)]

    def message_prev_user(self, chat_id: int, before_id: int):
        row = self._db.execute(
            "SELECT id, chat_id, who, text, ts, hue, lane, superseded FROM messages "
            "WHERE chat_id = ? AND who = 'cooper' AND superseded IS NULL AND id < ? ORDER BY id DESC LIMIT 1",
            (int(chat_id), int(before_id)),
        ).fetchone()
        return self._message_dict(row) if row else None

    def message_mark_superseded(self, message_id: int) -> None:
        """The ONLY update vault ever runs: the prior answer flags itself replaced (superseded = its own id)."""
        self._db.execute("UPDATE messages SET superseded = id WHERE id = ?", (int(message_id),))
        self._db.commit()

    def _message_dict(self, row) -> dict:
        mid, chat_id, who, text, ts, hue, lane, superseded = row
        return {"id": mid, "chat_id": chat_id, "who": who, "text": text, "ts": ts,
                "hue": hue, "lane": lane, "superseded": superseded}

    @property
    def path(self) -> Path:
        """Where this vault.db lives (the layer parks logs beside it by default)."""
        return self._path

    # --- clock workload (P-CORE-6): cancel = done flag, never DELETE — the trail stays auditable

    def reminder_insert(self, text: str, due_epoch: float, repeat: str = "", kind: str = "reminder") -> int:
        cur = self._db.execute(
            "INSERT INTO reminders (text, due_epoch, repeat, kind, done) VALUES (?, ?, ?, ?, 0)",
            (text, float(due_epoch), repeat, kind))
        self._db.commit()
        return cur.lastrowid

    def timer_insert(self, label: str, ends_epoch: float) -> int:
        cur = self._db.execute("INSERT INTO timers (label, ends_epoch, done) VALUES (?, ?, 0)",
                               (label, float(ends_epoch)))
        self._db.commit()
        return cur.lastrowid

    def due_reminders(self, now_epoch: float) -> list:
        rows = self._db.execute(
            "SELECT id, text, due_epoch, repeat, kind FROM reminders "
            "WHERE done = 0 AND due_epoch <= ? ORDER BY due_epoch ASC, id ASC", (float(now_epoch),))
        return [{"id": r[0], "text": r[1], "due_epoch": r[2], "repeat": r[3], "kind": r[4]} for r in rows]

    def due_timers(self, now_epoch: float) -> list:
        rows = self._db.execute(
            "SELECT id, label, ends_epoch FROM timers "
            "WHERE done = 0 AND ends_epoch <= ? ORDER BY ends_epoch ASC, id ASC", (float(now_epoch),))
        return [{"id": r[0], "label": r[1], "ends_epoch": r[2]} for r in rows]

    def reminder_done(self, rid: int) -> None:
        self._db.execute("UPDATE reminders SET done = 1 WHERE id = ?", (int(rid),))
        self._db.commit()

    def reminder_rearm(self, rid: int, new_due: float) -> None:
        self._db.execute("UPDATE reminders SET due_epoch = ? WHERE id = ?", (float(new_due), int(rid)))
        self._db.commit()

    def timer_done(self, tid: int) -> None:
        self._db.execute("UPDATE timers SET done = 1 WHERE id = ?", (int(tid),))
        self._db.commit()

    def next_pending_reminder(self, kind: str):
        row = self._db.execute(
            "SELECT id, text, due_epoch, kind FROM reminders WHERE done = 0 AND kind = ? "
            "ORDER BY due_epoch ASC, id ASC LIMIT 1", (kind,)).fetchone()
        return {"id": row[0], "text": row[1], "due_epoch": row[2], "kind": row[3]} if row else None

    def next_pending_timer(self):
        row = self._db.execute(
            "SELECT id, label, ends_epoch FROM timers WHERE done = 0 "
            "ORDER BY ends_epoch ASC, id ASC LIMIT 1").fetchone()
        return {"id": row[0], "label": row[1], "ends_epoch": row[2]} if row else None

    def clock_counts(self) -> dict:
        pending_r = self._db.execute("SELECT COUNT(*) FROM reminders WHERE done = 0").fetchone()[0]
        pending_t = self._db.execute("SELECT COUNT(*) FROM timers WHERE done = 0").fetchone()[0]
        return {"reminders_pending": pending_r, "timers_pending": pending_t}

    # --- people-book + sent ledger (P-CORE-7): 'forget' is a true DELETE (contacts are not a
    # ledger); sent_log is strictly append-only and journals successful sends ONLY — the
    # ledger records what left the box, never the intent.

    def contact_save(self, display: str, channel: str, value: str):
        """-> ("created"|"filled"|"dup", row|None). Name matches case-insensitively; an existing
        row only ever FILLS an empty channel — an occupied channel is a declared 'dup', never
        a silent overwrite. channel in {"telegram", "whatsapp"}."""
        existing = self.contact_get(display)
        if existing is None:
            col = {"telegram": "", "whatsapp": ""}
            col[channel] = str(value)
            cur = self._db.execute(
                "INSERT INTO contacts (name, telegram, whatsapp, added_on) VALUES (?, ?, ?, ?)",
                (str(display), col["telegram"], col["whatsapp"], _now()))
            self._db.commit()
            return "created", self.contact_get(display)
        if existing[channel]:
            return "dup", existing
        self._db.execute(f"UPDATE contacts SET {channel} = ? WHERE id = ?",
                         (str(value), existing["id"]))
        self._db.commit()
        return "filled", self.contact_get(display)

    def contact_get(self, name: str):
        row = self._db.execute(
            "SELECT id, name, telegram, whatsapp, added_on FROM contacts WHERE lower(name) = lower(?)",
            (str(name),)).fetchone()
        return self._contact_dict(row) if row else None

    def contact_remove(self, name: str):
        existing = self.contact_get(name)
        if existing is None:
            return None
        self._db.execute("DELETE FROM contacts WHERE id = ?", (existing["id"],))
        self._db.commit()
        return existing

    def contacts_list(self) -> list:
        rows = self._db.execute(
            "SELECT id, name, telegram, whatsapp, added_on FROM contacts ORDER BY id DESC").fetchall()
        return [self._contact_dict(r) for r in rows]

    def _contact_dict(self, row) -> dict:
        cid, name, telegram, whatsapp, added_on = row
        return {"id": cid, "name": name, "telegram": telegram, "whatsapp": whatsapp,
                "added_on": added_on}

    def sent_add(self, channel: str, recipient: str, kind: str, summary: str, sent_epoch: float) -> int:
        cur = self._db.execute(
            "INSERT INTO sent_log (channel, recipient, kind, summary, sent_epoch) VALUES (?, ?, ?, ?, ?)",
            (str(channel), str(recipient), str(kind), str(summary), float(sent_epoch)))
        self._db.commit()
        return int(cur.lastrowid)

    def sent_recall(self, name: str, limit: int = 5) -> list:
        """Newest-first, capped per finder-law — the honest recall row's source."""
        rows = self._db.execute(
            "SELECT id, channel, recipient, kind, summary, sent_epoch FROM sent_log "
            "WHERE lower(recipient) = lower(?) ORDER BY id DESC LIMIT ?",
            (str(name), int(limit))).fetchall()
        return [{"id": r[0], "channel": r[1], "recipient": r[2], "kind": r[3],
                 "summary": r[4], "sent_epoch": r[5]} for r in rows]

    def sent_count(self) -> int:
        return int(self._db.execute("SELECT COUNT(*) FROM sent_log").fetchone()[0])

    # ---------- P-CORE-12: the Leitner flashcard desk (bible §24) ----------
    def flash_add(self, front: str, back: str, due_epoch: float) -> int:
        cur = self._db.execute(
            "INSERT INTO flashcards (front, back, box, due_epoch) VALUES (?, ?, 1, ?)",
            (front, back, float(due_epoch)))
        self._db.commit()
        return int(cur.lastrowid)

    def flash_due(self, now_epoch: float) -> list:
        """Due cards, oldest-due first then by filing order — the review walks this order."""
        rows = self._db.execute(
            "SELECT id, front, back, box, due_epoch FROM flashcards WHERE due_epoch <= ? "
            "ORDER BY due_epoch, id", (float(now_epoch),)).fetchall()
        return [{"id": int(r[0]), "front": r[1], "back": r[2], "box": int(r[3]),
                 "due_epoch": float(r[4])} for r in rows]

    def flash_get(self, card_id: int):
        row = self._db.execute(
            "SELECT id, front, back, box, due_epoch FROM flashcards WHERE id = ?",
            (int(card_id),)).fetchone()
        if row is None:
            return None
        return {"id": int(row[0]), "front": row[1], "back": row[2], "box": int(row[3]),
                "due_epoch": float(row[4])}

    def flash_grade(self, card_id: int, box: int, due_epoch: float) -> None:
        """The grade re-files the card: new box, new due — professor.py owns the Leitner math."""
        self._db.execute("UPDATE flashcards SET box = ?, due_epoch = ? WHERE id = ?",
                         (int(box), float(due_epoch), int(card_id)))
        self._db.commit()

    def flash_count(self) -> int:
        return int(self._db.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0])

    def last_tars_text(self, chat_id=None):
        """Newest assistant message text (chat-scoped when an id rides along) — 'copy that''s source."""
        if chat_id is None:
            row = self._db.execute(
                "SELECT text FROM messages WHERE who = 'tars' ORDER BY id DESC LIMIT 1").fetchone()
        else:
            row = self._db.execute(
                "SELECT text FROM messages WHERE who = 'tars' AND chat_id = ? ORDER BY id DESC LIMIT 1",
                (int(chat_id),)).fetchone()
        return row[0] if row else None

    def wipe(self) -> None:
        """Part IX Handover: every personal table emptied in ONE transaction — the store is
        wholly pre-wipe or wholly post-wipe, never half. The schema stands; the rows were
        the person. There is no recovery path here by design (the farewell means it)."""
        with self._db:  # sqlite transaction: all tables or none
            for table in ("kv", "memory", "ledger", "chats", "messages",
                          "reminders", "timers", "contacts", "sent_log", "flashcards"):
                self._db.execute(f"DELETE FROM {table}")  # static names above — data never mixes in

    def integrity(self) -> str:
        return str(self._db.execute("PRAGMA integrity_check").fetchone()[0])

    def close(self) -> None:
        self._db.close()
