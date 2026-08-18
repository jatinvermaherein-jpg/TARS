"""The wake word — "Hey TARS".

Wake law: a detection fires ONLY through state.py — OFF -> summon -> ARMED ->
voice_start -> LISTENING (the only legal cold-wake path), or ARMED -> LISTENING
when the console is already up. A wake word heard while TARS is mid-turn
(LISTENING/THINKING/SPEAKING/ERROR) is ignored and logged; it never hijacks a
turn. Kill and idle laws are untouched — a wake is a summons, nothing more
(Law 3: no auto-start without the word; Law 5: the kill-switch stands above it).

PorcupineWakeEngine is the real Picovoice-style path (nt-guarded, lazy, custom
keyword file staged at M-1). FixtureWakeEngine scripts detections over voicefix
frames; it is the only engine the selftest drives.
"""
import os


class PorcupineWakeEngine:
    """Real keyword spotter — pvporcupine (Picovoice) behind a declared keyword file."""

    KEYWORD_FILE = "hey-tars.ppn"  # custom keyword, trained at the Picovoice console, staged at M-1

    def __init__(self, keyword_dir):
        self._path = keyword_dir / self.KEYWORD_FILE
        self._handle = None

    def load(self) -> bool:
        if self._handle is not None:
            return True
        if os.name != "nt":
            return False  # canon: the wake stack is staged on the AiO; the sandbox keeps fixtures
        if not self._path.exists():
            return False  # canon: the keyword file arrives at M-1; absent here, honestly unavailable
        try:
            import pvporcupine
        except ImportError:
            return False  # canon: M-1 staged dependency, never installed into a sandbox
        self._handle = pvporcupine.create(keyword_paths=[str(self._path)])
        return True

    def detect(self, frame: bytes) -> bool:
        import struct
        pcm = struct.unpack(f"<{len(frame) // 2}h", frame)  # pvporcupine processes native int16 frames
        return self._handle.process(pcm) >= 0


class FixtureWakeEngine:
    """Scripted wake spotter: detections pop in order, deterministic to the byte."""

    def __init__(self, scripted: list):
        self._script = list(scripted)
        self.calls = 0
        self.load_calls = 0

    def load(self) -> bool:
        self.load_calls += 1
        return True

    def detect(self, frame: bytes) -> bool:
        self.calls += 1
        return bool(self._script.pop(0))


def wake_turn(engine, frames: list, machine, log) -> dict:
    """One wake-watching window over captured frames. Detection applies through the
    state machine alone; an unavailable engine or a wake in a non-wake state changes
    nothing and leaves a log line instead."""
    if not engine.load():
        return {"awoken": False, "detected": False, "engine": "unavailable"}
    detected = any(engine.detect(frame) for frame in frames)
    if not detected:
        return {"awoken": False, "detected": False}
    if machine.state == "off":
        machine.summon()       # Law 3 honored by the word itself: no summon without it
        machine.voice_start()  # straight to LISTENING — the room asked for ears
        return {"awoken": True, "detected": True, "state": machine.state}
    if machine.state == "armed":
        machine.voice_start()
        return {"awoken": True, "detected": True, "state": machine.state}
    log.entry("wake", note=f"wake word ignored while {machine.state}: only OFF/ARMED may wake")
    return {"awoken": False, "detected": True, "state": machine.state}
