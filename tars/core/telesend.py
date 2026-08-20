"""TeleSend — the outbound engine (bible §17: two lanes, ONE gate).

The wires, in one place:
- USER LANE (default — sends AS Cooper): Telethon/MTProto, login-once session
  under TARS_DATA, api_id/api_hash ONLY via a caller-provided secrets mapping
  (the keys.py law: never auto-read env, never in the repo, never logged).
  `TelethonUserClient` is import-guarded optional — the psutil/whisper posture
  exactly: absent lib/session/credentials -> honest unlinked, ZERO wire
  attempts, and the canon not-linked line answers at the row.
- WhatsApp: the official `wa.me` text deep link. File-send stays OFF (a canon
  row, not a boundary — no unofficial path, no account risk).
- BOT lane: DEFERRED BY DECREE (elective on the roadmap; zero dead code beats
  a stub).

The TeleClient protocol both implementations speak (duck-typed, reviewable):
    linked() -> bool
    send_text(recipient, text) -> bool
    send_document(recipient, path) -> bool
No client method is ever called before a typed YES — the command layer stages,
shows the exact bytes, and only confirm() touches a wire. The battery proves
it with a call-recording fixture and a canary payload (SEND-CANARY pattern).
"""
import os
from pathlib import Path
from urllib.parse import quote

TELE_SESSION_FILE = "tars-telethon.session"


def wa_url(number: str, text: str) -> str:
    """The official wa.me deep link: digits only, payload urlencoded. TARS opens
    the door; the human's thumb presses send (the honest opened_ack says so)."""
    digits = "".join(ch for ch in str(number) if ch.isdigit())
    return f"https://wa.me/{digits}?text={quote(str(text), safe='')}"


def draft_prompt(ask: str, display: str) -> str:
    """The ONE lawful ring spend on a send row: Cooper asks TARS to compose.
    The ask is Cooper's own typed text; the drafted bytes come back and are
    staged verbatim for the gate — still Cooper's bytes to approve (§17)."""
    return (f"Write a short personal message for Telegram based on this request: \"{ask}\". "
            f"Recipient: {display}. Reply with ONLY the message text — no quotes, no preamble, "
            "no sign-off.")


class TelethonUserClient:
    """The REAL user lane. Every wire call is an nt-only seam (canon: the AiO is
    the home); off-nt, or without the optional telethon lib, session file, or
    caller-provided credentials, linked() is False and no send is attempted."""

    def __init__(self, data_dir, secrets=None):
        self._dir = Path(data_dir)
        self._secrets = dict(secrets or {})  # caller-provided mapping — keys.py posture

    def _creds(self):
        api_id = self._secrets.get("TELEGRAM_API_ID")
        api_hash = self._secrets.get("TELEGRAM_API_HASH")
        return (api_id, api_hash) if api_id and api_hash else None

    def _client(self):
        # canon: import inside the seam — telethon is never a sandbox dependency
        from telethon.sync import TelegramClient
        api_id, api_hash = self._creds()
        return TelegramClient(str(self._dir / TELE_SESSION_FILE), api_id, api_hash)

    def linked(self) -> bool:
        if os.name != "nt":
            return False  # canon: the real lane wakes on the AiO only
        try:
            import telethon  # noqa: F401 — presence probe, import-guarded
        except ImportError:
            return False
        return self._creds() is not None and (self._dir / TELE_SESSION_FILE).exists()

    def send_text(self, recipient: str, text: str) -> bool:
        if not self.linked():
            return False
        try:  # canon: a wire fault answers False — never a crash, never a retry storm
            with self._client() as client:
                client.send_message(recipient, text)
            return True
        except Exception:
            return False

    def send_document(self, recipient: str, path: str) -> bool:
        if not self.linked():
            return False
        try:
            with self._client() as client:
                client.send_file(recipient, str(path))
            return True
        except Exception:
            return False


class FixtureTelethon:
    """The suite's Telethon (roadmap acceptance: dry-run/mock). Records every
    (method, args) call in order; link state and per-method failures scripted."""

    def __init__(self, linked=True, fail=()):
        self._linked = bool(linked)
        self._fail = set(fail)
        self.calls = []

    def linked(self) -> bool:
        return self._linked

    def send_text(self, recipient: str, text: str) -> bool:
        self.calls.append(("send_text", recipient, str(text)))
        return "send_text" not in self._fail

    def send_document(self, recipient: str, path: str) -> bool:
        self.calls.append(("send_document", recipient, str(path)))
        return "send_document" not in self._fail
