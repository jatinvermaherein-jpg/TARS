"""The clock: reminders / alarms / timers, durable in the vault, fired by tick().

Natural time parse is DECLARED and closed (grammar v1.1): "in 20 minutes",
"at 6", "at 6:30 pm", "kal subah 7 baje" / "kal shaam 7 baje" (Hinglish set —
subah = morning, shaam = evening). Numbers ride grammar §0: digits or words.

tick(now_epoch) is the whole engine: driven by the state heartbeat in the app
era, driven by hand in the battery. Everything due fires once, in monotonic
due_epoch order, as a bus `reminder` event AND a returned row (the dialog
persists the line; the vault row flips done). Missed-while-OFF doctrine: a
reminder that fell due more than GRACE_S ago fires with "While you were away:
…" exactly once on next summon — never spam-batches. repeat="daily" re-arms
to the next future slot instead of dying.
"""
import re
from datetime import datetime, timedelta

from tars.core import canon

GRACE_S = 90  # on-time window: fire <= 90s after due reads as on-time, else away-wrapped
_DAY_S = 86400
_UNITS = {"second": 1, "seconds": 1, "minute": 60, "minutes": 60, "hour": 3600, "hours": 3600}
_PARTS = {"subah": "am", "shaam": "pm"}  # the closed Hinglish day-part set (kal <part> <H> baje)

_RE_IN = re.compile(r"^(?P<text>.+?) in (?P<num>\S+(?: \S+)?) (?P<unit>seconds?|minutes?|hours?)$")
_RE_AT = re.compile(r"^(?P<text>.+?) at (?P<hour>\d{1,2}|[a-z]+)(?::(?P<minute>\d{1,2}))?"
                    r"(?: (?P<ampm>am|pm))?$")
_RE_KAL = re.compile(r"^(?P<text>.+?) kal (?P<part>subah|shaam) (?P<hour>\S{1,12}) baje$")


def _number(token: str):
    """Digits or words 0..100 via canon (grammar §0); None when the token isn't a number."""
    return canon.words_number(token)


def _span_seconds(num: int, unit: str) -> int:
    return num * _UNITS[unit]


def _words_hour(hour: int, minute, ampm) -> str:
    """The echo shape for acks: 'six', 'six thirty pm', 'eighteen'."""
    words = canon.number_words(hour)
    if minute:
        words += f" {canon.number_words(minute)}"
    if ampm:
        words += f" {ampm}"
    return words


def parse_at(body: str, now: datetime):
    """'<text> at 6[:30][ pm]' / '<text> kal subah 7 baje' -> (text, epoch, echo) | None."""
    match = _RE_KAL.match(body)
    if match:
        part, hour = match.group("part"), _number(match.group("hour"))
        if hour is None or not 1 <= hour <= 12:
            return None
        target = (now + timedelta(days=1)).replace(hour=hour % 12 + (12 if part == "shaam" else 0),
                                                   minute=0, second=0, microsecond=0)
        echo = f"{_words_hour(hour, None, _PARTS[part])} tomorrow"
        return (match.group("text").strip(), target.timestamp(), echo)
    match = _RE_AT.match(body)
    if match:
        hour = _number(match.group("hour"))
        minute = int(match.group("minute")) if match.group("minute") else None
        ampm = match.group("ampm")
        if hour is None or not 0 <= hour <= 23 or (minute is not None and not 0 <= minute <= 59):
            return None
        spoken_hour = hour  # the echo keeps the user's clock-face — never 'eighteen' for 'six pm'
        if ampm:
            if not 1 <= hour <= 12:
                return None
            hour = hour % 12 + (12 if ampm == "pm" else 0)
        target = now.replace(hour=hour, minute=minute or 0, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)  # a clock time missed today lands tomorrow, never the past
        echo = _words_hour(spoken_hour, minute, ampm)
        return (match.group("text").strip(), target.timestamp(), echo)
    return None


def parse_reminder(body: str, now: datetime):
    """'call bhaiya in 20 minutes' / 'submit the form at 6:30 pm' / 'uthna kal subah 7 baje'
    -> (text, epoch, echo) | None."""
    match = _RE_IN.match(body)
    if match:
        num = _number(match.group("num"))
        if num is None or num < 1:
            return None
        unit = match.group("unit")
        seconds = _span_seconds(num, unit)
        echo = f"{canon.number_words(num)} {unit}"
        return (match.group("text").strip(), now.timestamp() + seconds, echo)
    return parse_at(body, now)


def parse_alarm(body: str, now: datetime):
    """'6:30' / '6:30 pm' / 'kal subah 7 baje' -> (epoch, echo) | None."""
    alias = f"bell {body}" if body.startswith("kal ") else f"bell at {body}"
    parsed = parse_at(alias, now)  # an alarm text rides the same clock shapes
    if parsed is None:
        return None
    _text, epoch, echo = parsed
    return epoch, echo


def parse_timer(body: str, now: datetime):
    """'timer for 5 minutes' / 'tea timer for 3 minutes' / bare '5 minutes' (timer lagao shape)
    -> (label, epoch, echo) | None."""
    label = ""
    rest = body
    if " timer for " in body:
        label, rest = body.split(" timer for ", 1)
    elif body.startswith("timer for "):
        rest = body[len("timer for "):]
    match = re.match(r"^(?P<num>\S+(?: \S+)?) (?P<unit>seconds?|minutes?|hours?)$", rest.strip())
    if not match:
        return None
    num = _number(match.group("num"))
    if num is None or num < 1:
        return None
    unit = match.group("unit")
    echo = f"{canon.number_words(num)} {unit}"
    return (label.strip(), now.timestamp() + _span_seconds(num, unit), echo)


class Clockd:
    """Durable clock engine: vault-owned rows, tick-driven firing, monotonic order."""

    def __init__(self, vault, bus, clock=None):
        self._vault = vault
        self._bus = bus
        self._clock = clock or datetime.now

    def tick(self, now_epoch: float = None) -> list:
        """Fire everything due, exactly once, monotonic in due time. -> fired rows (due order)."""
        moment = float(now_epoch if now_epoch is not None else self._clock().timestamp())
        due = []
        for row in self._vault.due_reminders(moment):
            due.append((row["due_epoch"], row["id"], "reminder", row))
        for row in self._vault.due_timers(moment):
            due.append((row["ends_epoch"], row["id"], "timer", row))
        due.sort(key=lambda item: (item[0], item[1]))
        fired = []
        for due_epoch, _id, family, row in due:
            if family == "timer":
                self._vault.timer_done(row["id"])
                line = canon.timer_fire_line(row["label"])
                detail = {"kind": "timer", "text": row["label"], "line": line, "due": due_epoch}
            else:
                if row["repeat"] == "daily":
                    new_due = row["due_epoch"]
                    while new_due <= moment:
                        new_due += _DAY_S  # re-arm to the NEXT future slot, never a batch of catch-ups
                    self._vault.reminder_rearm(row["id"], new_due)
                else:
                    self._vault.reminder_done(row["id"])
                line = (canon.alarm_fire_line(row["text"]) if row["kind"] == "alarm"
                        else canon.reminder_fire_line(row["text"]))
                detail = {"kind": row["kind"], "text": row["text"], "line": line, "due": due_epoch}
            away = moment - due_epoch > GRACE_S
            if away:
                line = canon.away_line(line)
                detail["line"] = line
            self._bus.emit("reminder", detail)
            fired.append(detail)
        return fired
