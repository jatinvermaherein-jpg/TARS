"""settings.json — the five command dials (bible §10).

HONESTY is hard-refused at every path: the dial-command path returns the
canon line, and even a hand-edited settings.json is forced back to ninety on
load, with a logged line. Writes are atomic tmp-then-rename; a corrupt file
recovers to factory defaults with a logged line instead of crashing.
"""
import json
import os
from pathlib import Path

from tars.core.canon import LINE_CATCH_ALL, LINE_HONESTY_FIXED, dial_line
from tars.core.logx import LogX

DIAL_DEFAULTS = {"humor": 5, "vernacular": 30, "discretion": 95, "trust": 25}
HONESTY_FIXED = 90


class Settings:
    """Load/save settings.json and execute dial moves under the bible's rules."""

    def __init__(self, path: Path, log: LogX, dials: dict):
        self._path = Path(path)
        self._log = log
        self._dials = dials

    @classmethod
    def load(cls, path: Path, log: LogX) -> "Settings":
        path = Path(path)
        if path.exists():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                dials = {name: int(raw["dials"][name]) for name in DIAL_DEFAULTS}
                if any(not 0 <= value <= 100 for value in dials.values()):
                    raise ValueError("dial out of range")
                if int(raw.get("honesty", HONESTY_FIXED)) != HONESTY_FIXED:
                    log.entry("error", cause="settings.json tried to move honesty; forced back to ninety")
                return cls(path, log, dials)
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                log.entry("error", cause=f"settings.json corrupt; factory defaults restored ({type(exc).__name__})")
        fresh = cls(path, log, dict(DIAL_DEFAULTS))
        fresh.save()
        return fresh

    @property
    def dials(self) -> dict:
        """The four movable dials, as a copy (HONESTY never leaves this class)."""
        return dict(self._dials)

    def reset_factory(self) -> None:
        """Part IX Handover: dials return to birth; HONESTY 90 never moves, here or anywhere."""
        self._dials = dict(DIAL_DEFAULTS)
        self.save()

    def save(self) -> None:
        """Atomic tmp-then-rename write (crash-safety rule for every TARS write)."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"honesty": HONESTY_FIXED, "dials": self._dials}, indent=2) + "\n"
        tmp = self._path.with_name(self._path.name + ".tmp")
        with open(tmp, "wb") as fh:  # wb: fsync needs a WRITE descriptor on nt (msvcrt _commit); an rb fd passes Linux, dies on Windows
            fh.write(payload.encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, self._path)

    def set_dial(self, name: str, value: int) -> dict:
        """Bridge-contract DialResult: {"ok": bool, "line": canon str}."""
        name = str(name).strip().lower()
        if name == "honesty":
            return {"ok": False, "line": LINE_HONESTY_FIXED}
        bad_value = isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100
        if name not in DIAL_DEFAULTS or bad_value:
            return {"ok": False, "line": LINE_CATCH_ALL}
        self._dials[name] = value
        self.save()
        self._log.entry("dial", name=name, value=value)
        return {"ok": True, "line": dial_line(name, value)}
