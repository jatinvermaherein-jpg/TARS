"""LOOK Mode — the session engine (bible §19, verbatim law).

Rolling captures every LOOK_INTERVAL_S (4s, inside the 3–5s band) through the
EXISTING dailyops screenshot seam (capture_frame — the same BitBlt capture,
returned as RAM bytes instead of a Desktop file; never a second capture path).

The buffer law (RAM Charter + privacy, battery-swept):
  at most 3 frames in memory, newest-wins discard, frames NEVER touch
  vault/disk — and a frame the classifier calls private never even enters
  the buffer. Rolling capture is NOT rolling spend: watching with no
  question and narration off makes ZERO adapter calls.

Session bounds — the §19 triad plus Law 5:
  STOP  ("enough" / "stop looking" rows) -> LINE_LOOK_OFF, buffer dropped
  IDLE  (no interaction for IDLE_S=600 — the tick drives the math) ->
        LINE_LOOK_IDLE, auto-off
  PANIC (the kill-switch from ANY state: lookd subscribes the standing bus
        "close" event — machine.kill() mid-watch drops the watcher and the
        buffer in the same instant, no dialog round-trip)
(On-hide lives bridge-side at P3 — declared in KNOWN LIMITS.)

Two-truths hue law: a frame-derived answer rides CLOUD amber with lane
"eyes" (cloud eyes saw it); the session ON/OFF/bounds lines ride LOCAL mint
(the deed is local).
"""
import base64

from tars.core import canon

LOOK_INTERVAL_S = 4   # the 3–5s band, one declared number
BUFFER_CAP = 3        # newest-wins; never persisted
IDLE_S = 600          # the truthful number behind LINE_LOOK_IDLE ("ten minutes")
STALE_S = 5           # a question answers about the LATEST frame only — fresher than this or we capture first

NARRATE_PROMPT = ("Describe what is on this screen in one or two plain sentences. "
                  "No preamble, no guesses about intent.")


class Lookd:
    """One look session: ops seam in, classifier gate before every byte outward."""

    def __init__(self, ops, classifier, router, bus, time_fn=None):
        import time as _time
        self._ops = ops
        self._classifier = classifier
        self._router = router
        self._time = time_fn or _time.time
        self._watching = False
        self._narrating = False
        self._frames = []          # RAM only — pytest-grade proof: nothing in here ever persists
        self._last_capture = 0.0
        self._last_interaction = 0.0
        bus.subscribe(self._on_bus_close)  # Law 5: panic rides the standing close event

    # ---------- lifecycle ----------

    @property
    def watching(self) -> bool:
        return self._watching

    @property
    def narrating(self) -> bool:
        return self._narrating

    @property
    def frame_count(self) -> int:
        return len(self._frames)

    def _on_bus_close(self, kind: str, detail: dict) -> None:
        if kind == "close" and (self._watching or self._frames):
            self._panic()

    def _panic(self) -> None:
        """Kill-switch bound: watcher dead instantly, buffer dropped, no speak."""
        self._watching = False
        self._narrating = False
        self._frames = []

    def start(self) -> str:
        now = self._time()
        self._frames = []
        self._watching = False
        frame = self._capture(now)  # the first capture is a REAL frame: classified, buffered or dropped
        if frame is False:
            return canon.LINE_LOOK_NO_SEAM  # seam honesty: never promise eyes that aren't there
        self._watching = True
        self._narrating = False
        self._last_interaction = now
        return canon.LINE_LOOK_ON

    def stop(self) -> str:
        self._watching = False
        self._narrating = False
        self._frames = []
        return canon.LINE_LOOK_OFF

    def narrate(self, on: bool) -> str:
        self._last_interaction = self._time()
        self._narrating = bool(on)
        return canon.LINE_NARRATE_ON if on else canon.LINE_NARRATE_OFF

    # ---------- the capture + gate (THE law) ----------

    def _capture(self, now: float):
        """Seam -> RAM frame -> CLASSIFY (every frame, before it counts) -> buffer or drop.
        Returns the buffered public frame, "private", or False (seam dead)."""
        shot = self._ops.capture_frame()
        if shot is False:
            return False
        png, title, text = shot
        frame = {"png": png, "title": title, "text": text, "stamp": now}
        self._last_capture = now  # a private frame still COST a capture — cadence truth
        if self._classifier.classify(frame) == "private":  # refused AT THE CLASSIFIER (§31)
            return "private"  # dropped immediately — never buffered, never sent, never persisted
        self._frames.append(frame)
        del self._frames[:-BUFFER_CAP]  # newest-wins, at most BUFFER_CAP held
        return frame

    # ---------- tick: rolling capture + narration + idle bound (clockd drives the call) ----------

    def tick(self, now_epoch=None) -> list:
        """-> [(text, hue, lane)] lines for the dialog to persist (idle-off mint / narration amber)."""
        if not self._watching:
            return []
        now = self._time() if now_epoch is None else now_epoch
        if now - self._last_interaction >= IDLE_S:
            self.stop()  # the same deeds, but the IDLE line speaks — mint, local
            return [(canon.LINE_LOOK_IDLE, "local", None)]
        lines = []
        if now - self._last_capture >= LOOK_INTERVAL_S:
            frame = self._capture(now)
            if frame not in (False, "private") and self._narrating:
                reply = self._router.route_vision(NARRATE_PROMPT, base64.b64encode(frame["png"]).decode("ascii"))
                for note in reply["notices"]:  # ring courtesy lines always render (standing law)
                    lines.append((note, "cloud", None))  # notices are rare by design
                lines.append((reply["text"], "cloud", reply["lane"]))
            # narration OFF + no question: ZERO adapter calls — rolling capture is not rolling spend
        return lines

    # ---------- the question door ----------

    def answer(self, question: str, now_epoch=None) -> dict:
        """A look-question: -> {"replies": [(text, hue, lane)], ...}. Never-List scanning is the
        caller's row (it fires pre-eyes). Freshness law: a stale/empty buffer captures first."""
        self._last_interaction = self._time() if now_epoch is None else now_epoch
        now = self._last_interaction
        frame = self._frames[-1] if self._frames else None
        if frame is None or now - frame["stamp"] > STALE_S:
            frame = self._capture(now)
        if frame is False:
            return {"replies": [(canon.LINE_LOOK_NO_SEAM, "local", None)]}
        if frame == "private":
            return {"replies": [(canon.LINE_PRIVATE_FRAME, "local", None)]}
        reply = self._router.route_vision(question, base64.b64encode(frame["png"]).decode("ascii"))
        notices = [(note, "cloud", None) for note in reply["notices"]]
        if not reply["ok"]:
            return {"replies": notices + [(reply["text"], "cloud", reply["lane"])]}
        return {"replies": notices + [(reply["text"], "cloud", reply["lane"])]}
