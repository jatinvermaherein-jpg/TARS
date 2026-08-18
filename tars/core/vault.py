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

    def integrity(self) -> str:
        return str(self._db.execute("PRAGMA integrity_check").fetchone()[0])

    def close(self) -> None:
        self._db.close()
