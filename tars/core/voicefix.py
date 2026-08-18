"""Voice fixtures — WAV bytes generated in code, pinned and deterministic.

Zero binary assets ever enter the repo (P-CORE-3 law): silence / sine-voiced /
noise segments are synthesized with stdlib math and wrapped as valid RIFF with
stdlib wave. Deterministic by construction (seeded noise), so VAD spans and
transcripts can be byte-pin-asserted. Used by the selftest now and reusable by
the P3/M-2 physical drills later.
"""
import io
import math
import random
import wave

RATE = 16000          # 16 kHz mono, the ears' diet
SINE_FREQ_HZ = 180    # a low, clearly-voiced hum
SINE_AMP = 8000       # RMS ~5657 — comfortably over the VAD threshold
NOISE_AMP = 200       # RMS ~115 — comfortably under it (noise is not speech)
FRAME_MS = 30         # mirrors ears.py so golden values stay honest


def silence_ms(duration_ms: int) -> bytes:
    return b"\x00\x00" * (RATE * duration_ms // 1000)


def sine_ms(duration_ms: int, freq: int = SINE_FREQ_HZ, amp: int = SINE_AMP) -> bytes:
    samples = RATE * duration_ms // 1000
    out = bytearray()
    for i in range(samples):
        value = int(amp * math.sin(2 * math.pi * freq * i / RATE))
        out += value.to_bytes(2, "little", signed=True)
    return bytes(out)


def noise_ms(duration_ms: int, amp: int = NOISE_AMP) -> bytes:
    rng = random.Random(7)  # pinned seed: noise bytes differ, energy never does
    samples = RATE * duration_ms // 1000
    out = bytearray()
    for _ in range(samples):
        out += rng.randint(-amp, amp).to_bytes(2, "little", signed=True)
    return bytes(out)


def pcm(parts: list) -> bytes:
    """Concatenate synthesized segments into one 16-bit PCM stream."""
    return b"".join(parts)


def wrap_wav(pcm_bytes: bytes, rate: int = RATE) -> bytes:
    """A valid mono 16-bit RIFF container around raw PCM (what the cloud ear eats)."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(pcm_bytes)
    return buffer.getvalue()
