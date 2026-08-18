"""Mic capture adapters — mic-cold law is ABSOLUTE: capture opens only while
the state machine sits in LISTENING, and closes on any exit path. The law is
enforced BEFORE any device is touched, on any OS. The visible mic indicator is
host/app duty (the app renders the LISTENING strip); this module owns the gate.

Real device open is Windows-first (`os.name == "nt"` adapter): the sounddevice
stack installs on the AiO at M-1; in a Linux sandbox the device path returns
False cleanly (canon comment on every skip). Tests drive FakeCapture.
"""
import os

# canon: real device bring-up is an M-1/P3 ceremony; the sandbox keeps the law, not the hardware.


class SoundDeviceCapture:
    """Real mic capture (sounddevice on the AiO). The law travels with it."""

    def __init__(self, machine, rate: int = 16000):
        self._machine = machine
        self._rate = rate
        self.closed = True

    def open(self) -> bool:
        if self._machine.state != "listening":
            raise RuntimeError("mic-cold law: capture opens only in LISTENING")
        if os.name != "nt":
            return False  # canon: no device probing in a Linux sandbox — M-1/P3 proves the hardware
        import sounddevice  # nt-guarded: present on the AiO after the M-1 staged pip table
        try:
            self._stream = sounddevice.RawInputStream(samplerate=self._rate, channels=1, dtype="int16")
            self._stream.start()
        except sounddevice.PortAudioError as exc:
            # canon: an OS-level device refusal maps to the §22 mic-denied row; the cause stays chained
            raise PermissionError("mic open refused by the OS") from exc
        self.closed = False
        return True

    def frames(self):
        """Yield 30ms PCM frames while open; the caller stops iterating on state change."""
        while not self.closed:
            data, _overflowed = self._stream.read(480)
            if self._machine.state != "listening":
                break
            yield bytes(data)

    def close(self) -> None:
        if not self.closed and os.name == "nt":
            self._stream.stop()
            self._stream.close()
        self.closed = True


class FakeCapture:
    """Scripted capture for the sandbox: frames pushed in code, law obeyed for real."""

    def __init__(self, machine, scripted_frames: list, on_frame=None, permission_denied: bool = False):
        self._machine = machine
        self._frames = list(scripted_frames)
        self._on_frame = on_frame
        self._permission_denied = permission_denied
        self.closed = True

    def open(self) -> bool:
        if self._machine.state != "listening":
            raise RuntimeError("mic-cold law: capture opens only in LISTENING")
        if self._permission_denied:
            raise PermissionError("mic open refused by the OS")  # scripted §22 mic-denied row
        self.closed = False
        return True

    def frames(self):
        for index, frame in enumerate(self._frames):
            if self.closed or self._machine.state != "listening":
                break
            if self._on_frame is not None:
                self._on_frame(index)  # test hook: e.g. kill the machine mid-stream
            yield frame

    def close(self) -> None:
        self.closed = True
