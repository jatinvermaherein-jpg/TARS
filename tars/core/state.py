"""The bible §32 state machine.

OFF ->(summon)-> ARMED ->(voice_start)-> LISTENING <-> THINKING <-> SPEAKING,
back to OFF via stand-down or 10 idle minutes. ERROR yields the prior state
and never traps. The kill-switch fires from ANY state, instantly. Mic law
(Law 5): mic_open is a pure function of state (true only in LISTENING), so a
killed or errored TARS can never hold the mic open.
"""
from datetime import datetime

from tars.core.bus import Bus
from tars.core.canon import LINE_CATCH_ALL
from tars.core.logx import LogX
from tars.core.settings import Settings

OFF = "off"
ARMED = "armed"
LISTENING = "listening"
THINKING = "thinking"
SPEAKING = "speaking"
ERROR = "error"

IDLE_LIMIT_S = 600  # bible §32: 10 idle minutes -> OFF


class Machine:
    """Transition guard + the single StateNotice emit path (contract §3)."""

    def __init__(self, settings: Settings, log: LogX, bus: Bus):
        self._settings = settings
        self._log = log
        self._bus = bus
        self._state = OFF
        self._error_prior = OFF
        self._error_cause = ""
        self._speaking_origin = ARMED  # text sessions return to ARMED, voice sessions to LISTENING
        self._lane = None
        self._hue = "local"
        self._audience = "cooper"  # Cooper ID lands in P-CORE-4; until then the operator is Cooper
        self._last_activity = datetime.now().timestamp()

    @property
    def state(self) -> str:
        return self._state

    @property
    def mic_open(self) -> bool:
        return self._state == LISTENING

    @property
    def audience(self) -> str:
        return self._audience

    def set_audience(self, audience: str) -> bool:
        """Tier the room (bible §22/§31) — the persona gate reads this and only this."""
        if audience not in ("cooper", "family", "guest"):
            self._log.entry("error", cause=f"ignored audience '{audience}'")
            return False
        if audience != self._audience:
            self._audience = audience
            self._log.entry("audience", tier=audience)
            self.emit_notice()
        return True

    def notice(self) -> dict:
        """Exact contract §3 StateNotice shape — the only way state is announced."""
        return {
            "state": self._state,
            "dials": self._settings.dials,
            "audience": self._audience,
            "lane": self._lane,
            "hue": self._hue,
        }

    def emit_notice(self) -> None:
        self._bus.emit("state", self.notice())

    def set_context(self, lane, hue: str) -> None:
        """Stamp the lane/hue of the reply currently being delivered."""
        self._lane = lane
        self._hue = hue

    def check_idle(self, now: float = None) -> bool:
        """True when ON and inactive for IDLE_LIMIT_S — the caller then stands down."""
        if self._state == OFF:
            return False
        moment = datetime.now().timestamp() if now is None else float(now)
        return (moment - self._last_activity) >= IDLE_LIMIT_S

    def summon(self) -> bool:
        return self._step(OFF, ARMED, "summon")

    def voice_start(self) -> bool:
        return self._step(ARMED, LISTENING, "mic open (push-to-talk/wake)")

    def heard(self) -> bool:
        if self._state != LISTENING:
            return self._invalid("heard")
        self._speaking_origin = LISTENING
        return self._go(THINKING, "utterance heard")

    def voice_stop(self) -> bool:
        return self._step(LISTENING, ARMED, "mic closed (push-to-talk released)")

    def text(self) -> bool:
        if self._state != ARMED:
            return self._invalid("text")
        self._speaking_origin = ARMED
        return self._go(THINKING, "typed message")

    def reply(self) -> bool:
        return self._step(THINKING, SPEAKING, "reply ready")

    def spoken(self) -> bool:
        if self._state != SPEAKING:
            return self._invalid("spoken")
        return self._go(self._speaking_origin, "reply complete")

    def stand_down(self, reason: str = "spoken") -> bool:
        if self._state in (OFF, ERROR):
            return self._invalid("stand_down")
        return self._go(OFF, f"stand down ({reason})")

    def fail(self, cause: str) -> bool:
        """Enter ERROR holding the prior state; the app hears a canon line."""
        if self._state == OFF:
            return self._invalid("fail")
        self._error_prior = self._state
        self._error_cause = cause
        self._bus.emit("error", {"code": "catch-all", "line": LINE_CATCH_ALL})
        return self._go(ERROR, f"error: {cause}")

    def recover(self) -> bool:
        if self._state != ERROR:
            return self._invalid("recover")
        return self._go(self._error_prior, f"recovered ({self._error_cause})")

    def kill(self) -> bool:
        """Law 5: instant, unconditional, from any state. Mic goes cold with the state."""
        if self._state == OFF:
            self._log.entry("kill-switch", result="already off")
            return True
        self._go(OFF, "kill-switch")
        self._bus.emit("close", {"reason": "kill-switch"})
        return True

    def _step(self, want_from: str, to: str, reason: str) -> bool:
        if self._state != want_from:
            return self._invalid(reason)
        return self._go(to, reason)

    def _go(self, new_state: str, reason: str) -> bool:
        old = self._state
        self._state = new_state
        self._last_activity = datetime.now().timestamp()
        self._log.entry("transition", **{"from": old, "to": new_state, "reason": reason})
        self.emit_notice()
        return True

    def _invalid(self, event: str) -> bool:
        self._log.entry("error", cause=f"ignored event '{event}' while {self._state}")
        return False
