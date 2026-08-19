"""The conversation service — the thing __main__, tests, and the P3 bridge
binding all call.

send() drives the state machine turn (text -> reply -> spoken), persists both
sides of the exchange into vault chats/messages, and since P-CORE-5 hands the
utterance to command.py FIRST: the grammar fast path (session/dial/memory/
operator rows) answers locally in milliseconds with zero ring spend; only a
non-match falls to the brain ring with the persona prompt (LIVE dials, never
cached) plus a rolling <=10-message window. Every reply chunk/done pair ends
with the A2 done-shape: {chatId, messageId, hue, lane}. quick_action pays the
A1 debt (read_aloud/redo), A3 (enroll_voice), and the ranked search pick; the
RED-verb typed-YES seam is confirm(actionId, yes) per contract §3.

Design declarations (also pinned in code comments where they live):
- chunk.seq restarts per message until true streaming lands.
- Brain-call hue is 'cloud' by construction; local replies (acks) are 'local'.
- Remember-intents are honored for audience == "cooper" only; family/guest
  payloads fall through to a memory-less brain answer (command.py keeps the
  same fall-through, behavior byte-for-byte).
- The P-CORE-2 dial/remember handlers moved to command.py (harness moved,
  behavior untouched); classify_memory stays importable from here.
"""
from tars.core import canon, enroll, persona
from tars.core.command import CommandLayer, classify_memory  # classify_memory: re-export, callers keep importing it from here
from tars.core.findfile import FileFinder, finder_roots_from_env
from tars.core.logx import LogX
from tars.core.operator import NtExecutor
from tars.core.searchlanes import SearchLanes

CONTEXT_WINDOW = 10  # rolling history cap per brain call
TITLE_CAP = 42


class Dialog:
    """One live conversation bound to machine, settings, router, vault and bus."""

    def __init__(self, settings, vault, router, machine, bus, voice_gate=None, command_layer=None):
        self._settings = settings
        self._vault = vault
        self._router = router
        self._machine = machine
        self._bus = bus
        self._voice_gate = voice_gate  # P-CORE-4 Cooper ID: typed passphrase restores Tier-1 mid-flow
        if command_layer is None:
            command_layer = CommandLayer(settings, vault, NtExecutor(), SearchLanes(),
                                         FileFinder(finder_roots_from_env()),
                                         LogX(vault.path.parent / "logs.jsonl"), bus)
        self._command = command_layer
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
        self._machine.text()
        self._dispatch(str(text))
        return {"chatId": self._chat_id}

    def send_voice(self, text) -> dict:
        """Voice entry: ears own capture + heard(); the dialog takes over from THINKING."""
        if self._machine.state != "thinking":
            return {"ok": False, "line": canon.LINE_CATCH_ALL}
        if self._chat_id is None:
            self.new_chat()
        self._dispatch(str(text))
        return {"chatId": self._chat_id}

    def _dispatch(self, text: str) -> None:
        self._machine.reply()
        if self._voice_gate is not None and self._voice_gate.try_passphrase(text, self._machine):
            self._emit_message(canon.LINE_VERIFIED, "local", None)
            self._machine.spoken()
            return  # §22: a correct pass restores Tier-1 — the pass text never persists, never routes
        user_mid = self._vault.message_add(self._chat_id, "cooper", text, None, None)
        plan = self._command.execute(str(text), self._machine)
        if plan["handled"]:
            if plan["new_chat"]:
                self.new_chat()  # the boot line opens the FRESH chat; the command itself closed the old one
            for line, hue, lane in plan["replies"]:
                self._emit_message(line, hue, lane)
            self._machine.spoken()
            if plan["stand_down"]:
                self._machine.stand_down("spoken")
                self._bus.emit("close", {"reason": "stand down"})
            return
        self._brain_turn(text, user_mid)  # (8) else: the ring is conversation's home
        self._machine.spoken()

    def confirm(self, action_id, yes: bool = False) -> dict:
        """Contract §3 typed-YES seam: releases a parked RED verb exactly once; the
        outcome persists like every response. Unknown/expired ids answer LINE_CANCEL."""
        result = self._command.confirm(str(action_id), bool(yes))
        if self._chat_id is None:
            self.new_chat()
        self._emit_message(result["line"], "local", None)
        return {"ok": result["ok"], "line": result["line"]}

    def emit_line(self, line: str, hue: str = "local") -> int:
        """A §22-family canon line as a persisted tars message (called from THINKING)."""
        if self._chat_id is None:
            self.new_chat()  # a line must persist into a real chat, never a null row
        self._machine.reply()
        mid = self._emit_message(line, hue, None)
        self._machine.spoken()
        return mid

    def quick_action(self, name, payload) -> dict:
        payload = payload or {}
        if name == "read_aloud":
            return self._read_aloud(payload)
        if name == "redo":
            return self._redo(payload)
        if name == "enroll_voice":
            if payload:  # A3: enroll_voice takes payload {} exactly — anything else never guesses
                return {"ok": False, "line": canon.LINE_CATCH_ALL}
            return enroll.open_wizard()
        if name == "open":
            return self._open_rank(payload)  # the ranked search pick ("open the second") — P-CORE-5
        return {"ok": False, "line": canon.LINE_CATCH_ALL}

    def _emit_message(self, text: str, hue, lane) -> int:
        """Persist a tars message and stream it: chunk (seq restarts per message) + A2 done."""
        mid = self._vault.message_add(self._chat_id, "tars", text, hue, lane)
        self._machine.set_context(lane, hue)
        self._bus.emit("chunk", {"chatId": self._chat_id, "seq": 0, "text": text})
        self._bus.emit("done", {"chatId": self._chat_id, "messageId": mid, "hue": hue, "lane": lane})
        return mid

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

    def _open_rank(self, payload) -> dict:
        try:
            rank = int(payload.get("rank"))
        except (AttributeError, TypeError, ValueError):
            return {"ok": False, "line": canon.LINE_CATCH_ALL}  # no rank, never a guess
        picked = self._command.open_rank(rank)
        if picked is None:
            return {"ok": False, "line": canon.LINE_CATCH_ALL}  # no search behind it, never a guess
        if self._chat_id is None:
            self.new_chat()
        self._emit_message(picked["line"], "cloud", None)  # response law: even picks persist + stream
        return {"ok": True, "rank": picked["rank"], "title": picked["title"], "url": picked["url"],
                "line": picked["line"]}

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
