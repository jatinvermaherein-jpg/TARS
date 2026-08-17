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
"""


def _now() -> str:
    return datetime.now().isoformat(timespec="milliseconds")


class Vault:
    """Crash-safe local store: kv state, journal memory, quota ledger."""

    def __init__(self, path: Path):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(self._path))
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

    def integrity(self) -> str:
        return str(self._db.execute("PRAGMA integrity_check").fetchone()[0])

    def close(self) -> None:
        self._db.close()
