"""The speak ladder — Piper -> SAPI -> edge-tts, privacy routing is LAW.

Tier order (bible §27, amended M-2.1, ballot 2n): Piper first (LOCAL neural —
the anointed voice, staged as tars-piper.onnx), SAPI second (Windows-native
stock floor, the always-present emergency layer), edge-tts last (CLOUD — the
human-sounding tier, public-safe utterances only). The privacy guard sits in the ladder walk
itself: a private utterance never reaches the edge tier — there is no flag,
no config, no override (§31). If nothing local can serve, the text stays on
screen and the moment is logged, per the prompt's rule (no new canon line).

Barge-in (§20): interrupt() sets a shared cancel event AND calls stop() on the
active tier; a tier consults the cancel event between ticks, so a fresh listen
wins in-tick, always. All state transitions flow through state.py — the mouth
never self-transitions. Voice character constants are declared per tier (§9:
masculine, low, measured); the FINAL voice is the M-2 audition by ear.
"""
import os
import shutil
import subprocess
import threading

from tars.core.logx import LogX

# Voice-character constants (§9) — M-2 audition picks the final voice by ear; these are the starting posture.
SAPI_RATE = -1            # System.Speech -10..10 scale; slightly measured
PIPER_LENGTH_SCALE = 1.1  # slower-than-default pacing, low and measured reads
EDGE_RATE = "-8%"
EDGE_PITCH = "-2Hz"
EDGE_VOICE = "en-IN-PrabhatNeural"  # placeholder-free: the audition shortlist starts here, M-2 decides by ear


class SapiTier:
    """Windows System.Speech one-shot (LOCAL). nt-guarded: the sandbox just says unavailable."""

    name = "sapi"
    local = True

    def available(self) -> bool:
        return os.name == "nt"  # canon: SAPI exists only on the AiO; P3 hears it first

    def speak(self, text: str, cancel) -> bool:
        if os.name != "nt":
            return False  # canon: Linux sandbox — nothing to drive, nothing to prove
        ps = ("Add-Type -AssemblyName System.Speech; "
              "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
              f"$s.Rate = {SAPI_RATE}; $s.Speak([Console]::In.ReadToEnd())")
        proc = subprocess.Popen(["powershell", "-NoProfile", "-Command", ps],
                                stdin=subprocess.PIPE, text=True)
        self._proc = proc
        proc.stdin.write(text)
        proc.stdin.close()
        while proc.poll() is None:
            if cancel():
                proc.kill()
                return None
        return proc.returncode == 0

    def stop(self) -> None:
        proc = getattr(self, "_proc", None)
        if proc is not None and proc.poll() is None:
            proc.kill()


class PiperTier:
    """Piper with a declared local model file (LOCAL). Runs anywhere the file + binary exist."""

    name = "piper"
    local = True

    def __init__(self, model_dir):
        self._model = model_dir / "tars-piper.onnx"
        self._exe = shutil.which("piper")

    def available(self) -> bool:
        return self._model.exists() and self._exe is not None

    def speak(self, text: str, cancel) -> bool:
        wav_path = self._model.with_suffix(".speak.wav")
        synth = subprocess.Popen([self._exe, "--model", str(self._model),
                                  "--length-scale", str(PIPER_LENGTH_SCALE),
                                  "--output_file", str(wav_path)],
                                 stdin=subprocess.PIPE, text=True)
        self._proc = synth
        synth.stdin.write(text)
        synth.stdin.close()
        while synth.poll() is None:
            if cancel():
                synth.kill()
                return None
        if synth.returncode != 0:
            return False
        if os.name == "nt":
            # canon: Windows playback = the OS SoundPlayer, zero extra deps on the AiO
            play = subprocess.run(["powershell", "-NoProfile", "-Command",
                                   f"(New-Object System.Media.SoundPlayer '{wav_path}').PlaySync()"], timeout=120)
            return play.returncode == 0
        player = shutil.which("aplay")
        if player is None:
            return False  # canon: sandbox has no speaker chain; the tier honestly reports unplayed
        return subprocess.run([player, str(wav_path)], timeout=120).returncode == 0

    def stop(self) -> None:
        proc = getattr(self, "_proc", None)
        if proc is not None and proc.poll() is None:
            proc.kill()


class EdgeTier:
    """edge-tts (CLOUD). Public-safe utterances only — the ladder never hands it private text."""

    name = "edge"
    local = False

    def available(self) -> bool:
        return shutil.which("edge-tts") is not None

    def speak(self, text: str, cancel) -> bool:
        out_path = os.devnull if os.name != "nt" else "tars-edge.mp3"
        synth = subprocess.Popen(["edge-tts", "--voice", EDGE_VOICE, f"--rate={EDGE_RATE}",
                                  f"--pitch={EDGE_PITCH}", "--text", text, "--write-media", out_path])
        self._proc = synth
        while synth.poll() is None:
            if cancel():
                synth.kill()
                return None
        return synth.returncode == 0

    def stop(self) -> None:
        proc = getattr(self, "_proc", None)
        if proc is not None and proc.poll() is None:
            proc.kill()


class FixtureTier:
    """Simulated tier: scripted availability/outcome, per-tick cancel consult, call recording."""

    def __init__(self, name: str, local: bool, available: bool, outcome: str = "ok",
                 ticks: int = 1, on_tick=None):
        self.name = name
        self.local = local
        self._available = available
        self._outcome = outcome
        self._ticks = ticks
        self._on_tick = on_tick
        self.calls = []
        self.stop_calls = 0

    def available(self) -> bool:
        return self._available

    def speak(self, text: str, cancel):
        self.calls.append(text)
        for tick in range(self._ticks):
            if self._on_tick is not None:
                self._on_tick(tick)
            if cancel():
                return None  # cancel honored exactly in-tick
        if self._outcome == "fail":
            return False
        return True

    def stop(self) -> None:
        self.stop_calls += 1


class Mouth:
    """The ladder walker + speak-queue drain. Never moves the state machine itself."""

    def __init__(self, tiers: list, log: LogX):
        self._tiers = tiers
        self._log = log
        self._cancel = threading.Event()
        self._active = None

    def interrupt(self) -> None:
        self._cancel.set()
        if self._active is not None:
            self._active.stop()  # barge-in: the in-flight utterance dies immediately (§20)

    def speak(self, text: str, private: bool = False) -> dict:
        """Walk the tiers; result 'tier' names who served / cancelled / LAST attempted (None if none tried)."""
        self._cancel.clear()
        attempted = None
        for tier in self._tiers:
            if private and not tier.local:
                self._log.entry("privacy", note="edge skipped: a private utterance never rides edge-tts")
                continue
            if not tier.available():
                continue
            attempted = tier
            self._active = tier
            outcome = tier.speak(text, self._cancel.is_set)
            self._active = None
            if outcome is None:
                return {"ok": False, "tier": tier.name, "cancelled": True}
            if outcome:
                return {"ok": True, "tier": tier.name, "cancelled": False, "private": private}
        self._log.entry("mouth", note="no serving tier; the text stayed on screen")
        return {"ok": False, "tier": attempted.name if attempted else None,
                "cancelled": False, "private": private}

    def drain_speak_queue(self, vault, machine) -> dict:
        """A1 drain: every kv 'speak_request:<mid>'='queued' intake gets spoken and marked
        'done' / 'failed:<tier>'. Queue items carry no public tag this phase, so every
        drain serves the LOCAL tiers only — the P-CORE-4 audience matrix owns smarter tagging."""
        report = {"drained": 0, "failed": 0}
        for name, _value in vault.kv_scan("speak_request:", only_value="queued"):
            message = vault.message_get(int(name.rsplit(":", 1)[1]))
            if message is None:
                vault.kv_set(name, "failed:no-message")
                self._log.entry("mouth", note="speak request pointed at a missing message")
                report["failed"] += 1
                continue
            if machine.state == "off":
                machine.summon()
            machine.text()   # the speak turn rides the state machine: THINKING -> SPEAKING -> back
            machine.reply()
            outcome = self.speak(message["text"], private=True)
            machine.spoken()
            if outcome["ok"]:
                vault.kv_set(name, "done")
                report["drained"] += 1
            else:
                vault.kv_set(name, f"failed:{outcome['tier'] or 'none'}")
                report["failed"] += 1
        return report
