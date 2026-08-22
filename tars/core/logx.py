"""logs.jsonl — append-only JSON-lines log, fsync'd after every entry (bible §30).

Every state transition, dial change and error lands here; the file survives a
power cut up to the last fsync'd line, and a torn tail line left by a kill is
detected on read (json parse failure = corruption flag, never a crash).
"""
import json
import os
from datetime import datetime
from pathlib import Path


class LogX:
    """Append-only writer + parse-back reader for logs.jsonl."""

    def __init__(self, path: Path):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.touch()  # the log exists from birth; no standing handle owed

    def entry(self, kind: str, **fields) -> dict:
        """Append one fsync'd record; returns the record written."""
        record = {"ts": datetime.now().isoformat(timespec="milliseconds"), "kind": kind, **fields}
        # P-CORE-12N: open -> write -> fsync -> close PER ENTRY. A standing append handle
        # blocks the handover wipe's os.replace on nt (WinError 5: no rename over an open
        # file); POSIX forgives the collision, Windows-first law never holds what another
        # seam must be free to move.
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        return record

    def read_all(self) -> list:
        """Parse every line back; a corrupt tail line raises ValueError so callers can flag it."""
        if not self._path.exists():
            return []
        return [json.loads(line) for line in self._path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def count(self) -> int:
        return len(self.read_all())

    def close(self) -> None:
        """Advisory seam: handles are per-entry (12N), so nothing stands open to release."""
