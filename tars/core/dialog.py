"""The conversation service — the thing __main__, tests, and the P3 bridge
binding all call.

send() drives the state machine turn (text -> reply -> spoken), persists both
sides of the exchange into vault chats/messages, classifies the intent in
order: dial command -> remember-intent -> brain call. Brain calls ride the
persona system prompt (built from LIVE dials, never cached) plus a rolling
<=10-message window of this chat. Every reply chunk/done pair ends with the
A2 done-shape: {chatId, messageId, hue, lane}. quick_action pays the A1 debt:
read_aloud intake + redo regeneration with the superseded flag.

Design declarations (also pinned in code comments where they live):
- chunk.seq restarts per message until true streaming lands.
- Brain-call hue is 'cloud' by construction; local replies (acks) are 'local'.
- Remember-intents are honored for audience == "cooper" only; with no canon
  refusal line for it, family/guest payloads fall through to a memory-less
  brain answer (documented in build-log too).
"""
from tars.core import canon, persona

DIAL_NAMES = ("humor", "vernacular", "discretion", "trust", "honesty")
REMEMBER_PATTERNS = ("remember this", "remember that", "note that", "yaad rakh")
PERSON_WORDS = ("ma", "papa", "bhaiya", "didi", "friend", "teacher", "sir", "uncle", "aunty")
PLAN_WORDS = ("plan", "tomorrow", "remind", "exam", "test", "deadline", "result")
PREFERENCE_WORDS = ("prefer", "prefers", "like", "likes", "love", "loves", "favorite", "favourite",
                    "hate", "hates", "dislike", "dislikes")
CONTEXT_WINDOW = 10  # rolling history cap per brain call
TITLE_CAP = 42


def classify_memory(payload: str) -> str:
    """Declared rule order: person -> plan -> preference -> fact (first word-hit wins)."""
    words = set(payload.lower().replace(".", " ").replace(",", " ").split())
    if words & set(PERSON_WORDS):
        return "person"
    if words & set(PLAN_WORDS):
        return "plan"
    if words & set(PREFERENCE_WORDS):
        return "preference"
    return "fact"


def parse_dial_command(text: str):
    """'<dial> <int>' -> (name, value); a bad number rides as None into set_dial's refusal."""
    parts = text.strip().lower().split()
    if len(parts) == 2 and parts[0] in DIAL_NAMES:
        try:
            return parts[0], int(parts[1])
        except ValueError:
            return parts[0], None
    return None


def remember_payload(text: str):
    """Declared pattern list (English + Hinglish basics). Empty payload -> normal chat."""
    lowered = text.strip().lower()
    for pattern in REMEMBER_PATTERNS:
        if lowered.startswith(pattern):
            payload = text.strip()[len(pattern):].lstrip(" :,-").strip()
            return payload or None
    return None


class Dialog:
    """One live conversation bound to machine, settings, router, vault and bus."""

    def __init__(self, settings, vault, router, machine, bus):
        self._settings = settings
        self._vault = vault
        self._router = router
        self._machine = machine
        self._bus = bus
        self._chat_id = None

    def new_chat(self) -> dict:
        self._chat_id = self._vault.chat_insert()
        return {"id": self._chat_id}

    def list_chats(self) -> list:
        summaries = []
        for row in reversed(self._vault.chat_rows()):  # sidebar order: newest first
            first = self._vault.chat_first_user_text(row["id"])
            title = "New chat" if first is None else (first if len(first) <= TITLE_CAP
                                                      else first[:TITLE_CAP].rstrip() + "...")
            summaries.append({"id": row["id"], "title": title, "ts": row["created"],
                              "lastHue": self._vault.chat_last_hue(row["id"])})
        return summaries

    def open_chat(self, chat_id) -> list:
        return [{"id": m["id"], "who": m["who"], "text": m["text"], "ts": m["ts"], "hue": m["hue"],
                 "lane": m["lane"], "actions": ["copy", "read_aloud", "redo"]}
                for m in self._vault.messages_for(int(chat_id))]

    def send(self, text) -> dict:
        if self._machine.state == "off":
            self._machine.summon()  # a bridge send implies a summoned app
        if self._chat_id is None:
            self.new_chat()
        text = str(text)
        self._machine.text()
        user_mid = self._vault.message_add(self._chat_id, "cooper", text, None, None)
        self._machine.reply()
        dial = parse_dial_command(text)
        if dial is not None:
            self._emit_message(self._dial_line(*dial), "local", None)
        else:
            payload = remember_payload(text)
            if payload is not None and self._machine.audience == "cooper":
                self._vault.remember(classify_memory(payload), payload)
                self._emit_message(canon.LINE_NOTED, "local", None)
            else:
                self._brain_turn(text, user_mid)
        self._machine.spoken()
        return {"chatId": self._chat_id}

    def quick_action(self, name, payload) -> dict:
        payload = payload or {}
        if name == "read_aloud":
            return self._read_aloud(payload)
        if name == "redo":
            return self._redo(payload)
        return {"ok": False, "line": canon.LINE_CATCH_ALL}

    def _emit_message(self, text: str, hue, lane) -> int:
        """Persist a tars message and stream it: chunk (seq restarts per message) + A2 done."""
        mid = self._vault.message_add(self._chat_id, "tars", text, hue, lane)
        self._machine.set_context(lane, hue)
        self._bus.emit("chunk", {"chatId": self._chat_id, "seq": 0, "text": text})
        self._bus.emit("done", {"chatId": self._chat_id, "messageId": mid, "hue": hue, "lane": lane})
        return mid

    def _dial_line(self, name, value) -> str:
        if self._machine.audience != "cooper":
            return canon.LINE_GUEST_DIAL  # §10: only Cooper's verified voice or the panel moves dials
        result = self._settings.set_dial(name, value)
        if result["ok"]:
            self._machine.emit_notice()  # dials move live mid-conversation: fresh StateNotice
        return result["line"]

    def _dial_snapshot(self) -> dict:
        snapshot = {"honesty": 90}
        snapshot.update(self._settings.dials)
        return snapshot

    def _system_prompt(self) -> str:
        audience = self._machine.audience
        memories = self._vault.recall()[-8:] if audience == "cooper" else []
        return persona.build_system_prompt(self._dial_snapshot(), audience, memories)

    def _brain_turn(self, text: str, user_mid: int) -> None:
        history = [{"role": ("user" if m["who"] == "cooper" else "assistant"), "content": m["text"]}
                   for m in self._vault.message_context(self._chat_id, user_mid, CONTEXT_WINDOW)]
        reply = self._router.route(text, system_prompt=self._system_prompt(), history=history)
        for notice in reply["notices"]:
            self._emit_message(notice, "cloud", None)
        self._emit_message(reply["text"], "cloud", reply["lane"])

    def _ids(self, payload):
        try:
            return int(payload["chatId"]), int(payload["messageId"])
        except (KeyError, TypeError, ValueError):
            return None

    def _read_aloud(self, payload) -> dict:
        ids = self._ids(payload)
        message = self._vault.message_get(ids[1]) if ids else None
        if message is None or message["chat_id"] != (ids[0] if ids else None):
            return {"ok": False, "line": canon.LINE_CATCH_ALL}  # bad ids: never guess a target
        self._vault.kv_set(f"speak_request:{message['id']}", "queued")  # declared intake; the mouth drains it in P-CORE-3
        return {"ok": True, "chatId": ids[0], "text": message["text"], "messageId": message["id"]}

    def _redo(self, payload) -> dict:
        ids = self._ids(payload)
        message = self._vault.message_get(ids[1]) if ids else None
        if message is None or message["chat_id"] != (ids[0] if ids else None) or message["who"] != "tars":
            return {"ok": False, "line": canon.LINE_CATCH_ALL}  # bad target: never guess
        user_message = self._vault.message_prev_user(ids[0], message["id"])
        if user_message is None:
            return {"ok": False, "line": canon.LINE_CATCH_ALL}  # nothing to regenerate from
        if self._machine.state == "off":
            self._machine.summon()
        self._machine.text()
        self._machine.reply()
        history = [{"role": ("user" if m["who"] == "cooper" else "assistant"), "content": m["text"]}
                   for m in self._vault.message_context(ids[0], user_message["id"], CONTEXT_WINDOW)]
        reply = self._router.route(user_message["text"], system_prompt=self._system_prompt(), history=history)
        notice_marks = 0
        for notice in reply["notices"]:
            self._emit_message(notice, "cloud", None)
            notice_marks += 1
        new_mid = self._emit_message(reply["text"], "cloud", reply["lane"])
        self._vault.message_mark_superseded(message["id"])  # after the insert: on a crash mid-redo we duplicate, never lose
        self._machine.spoken()
        return {"ok": True, "chatId": ids[0], "messageId": new_mid}
