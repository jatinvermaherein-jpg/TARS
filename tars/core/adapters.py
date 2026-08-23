"""Provider adapters — byte-exact request signatures, fixture twin for all tests.

The real classes (GroqAdapter / OpenRouterAdapter) carry the full urllib
codepath — written, reviewable, and never network-called in a sandbox: with
no key string they return the canon refusal dict instead of touching the wire
(first live call is the P3 ceremony on the AiO, roadmap §4). FixtureAdapter
implements the identical interface from recorded scripts and is the ONLY
adapter the selftest drives.
"""
import json
import re
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from tars.core import canon

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
TIMEOUT_S = 30  # bible §26: 30-second ceiling, then retry on the next healthy key

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _speakable(text: str) -> str:
    """Reasoning-class models (gpt-oss, qwen3.6) wrap their chain-of-thought in a
    <think>…</think> envelope INSIDE the content bytes (field-true at the P3.4
    eyes ceremony, Aug 23). The scaffolding is never TARS's voice — strip every
    envelope, keep the verdict. Never invent: if only scaffolding came back, the
    raw text stands rather than an empty reply."""
    stripped = _THINK_RE.sub("", text).strip()
    return stripped or text.strip()


@dataclass
class AdapterResult:
    text: str = ""
    tokens: int = 0
    latency_ms: int = 0
    key_visible_name: str = ""
    ok: bool = False
    error: str = None  # None | "timeout" | "http_429" | "http_5xx" | "garbage_json" | "no_keys"


def _http_call(url: str, messages: list, *, key_string: str, key_visible_name: str, model: str,
               timeout_s: int) -> AdapterResult:
    if not key_string:
        # No key, no wire: the refusal dict, not a crash.
        return AdapterResult(text=canon.LINE_ALL_SPENT, key_visible_name=key_visible_name, error="no_keys")
    payload = json.dumps({"model": model, "messages": messages}).encode("utf-8")
    request = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization": f"Bearer {key_string}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        # The honest nametag: bare-stdlib requests die at the provider's edge gate
        # (Cloudflare error 1010, signature ban on bot-shaped traffic — the doctor
        # proved it field-true 2026-08-23). Self-identification is Never-List-clean:
        # we declare what we are, we never impersonate a browser.
        "User-Agent": "tars-core/1.0 (resident, Cooper's machine)",
    })
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            body = json.loads(response.read().decode("utf-8"))
        return AdapterResult(
            text=_speakable(body["choices"][0]["message"]["content"]),
            tokens=int(body.get("usage", {}).get("total_tokens", 0)),
            latency_ms=int((time.monotonic() - started) * 1000),
            key_visible_name=key_visible_name,
            ok=True,
        )
    except urllib.error.HTTPError as exc:
        # 429 is rate-limited; every other HTTP fault rides the retry as a 5xx-class failure.
        return AdapterResult(key_visible_name=key_visible_name,
                             error="http_429" if exc.code == 429 else "http_5xx")
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, OSError):
        return AdapterResult(key_visible_name=key_visible_name, error="timeout")
    except (json.JSONDecodeError, KeyError, IndexError, UnicodeDecodeError):
        return AdapterResult(key_visible_name=key_visible_name, error="garbage_json")


class GroqAdapter:
    """Groq chat-completions endpoint (fast/smart/eyes/ears lanes)."""

    def call(self, messages: list, *, key_string: str, key_visible_name: str, model: str,
             timeout_s: int = TIMEOUT_S) -> AdapterResult:
        return _http_call(GROQ_URL, messages, key_string=key_string, key_visible_name=key_visible_name,
                          model=model, timeout_s=timeout_s)


class OpenRouterAdapter:
    """OpenRouter chat-completions endpoint (ultra/council lanes)."""

    def call(self, messages: list, *, key_string: str, key_visible_name: str, model: str,
             timeout_s: int = TIMEOUT_S) -> AdapterResult:
        return _http_call(OPENROUTER_URL, messages, key_string=key_string, key_visible_name=key_visible_name,
                          model=model, timeout_s=timeout_s)


class FixtureAdapter:
    """Scripted twin of the real adapters. Each call pops one scripted step and
    records the exact `messages` list it received (self.received) for assertions.
    The AdapterResult contract is unchanged."""

    def __init__(self, provider: str, script: list, by_model: dict = None):
        self.provider = provider
        self._script = list(script)
        # P-CORE-12: council seats run in PARALLEL threads, so a FIFO script's pop order
        # would race seat-to-lane assignment; by_model gives each declared model slug its
        # own queue — the verdict battery scripts deterministically (empty queue pops loud).
        self._by_model = {model: list(steps) for model, steps in by_model.items()} if by_model else None
        self.received = []
        self.received_models = []  # call order as seen on the wire (lanes proven against it)

    def call(self, messages: list, *, key_string: str, key_visible_name: str, model: str,
             timeout_s: int = TIMEOUT_S) -> AdapterResult:
        self.received.append([dict(message) for message in messages])
        self.received_models.append(model)
        queue = self._by_model[model] if self._by_model is not None else self._script
        step = queue.pop(0)
        if step[0] == "ok":
            _, text, tokens = step
            return AdapterResult(text=text, tokens=int(tokens), latency_ms=0,
                                 key_visible_name=key_visible_name, ok=True)
        return AdapterResult(key_visible_name=key_visible_name, error=step[0])
