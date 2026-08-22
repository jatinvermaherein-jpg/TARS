"""The conversation service — the thing __main__, tests, and the P3 bridge
binding all call.

send() drives the state machine turn (text -> reply -> spoken), persists both
sides of the exchange into vault chats/messages, and since P-CORE-5 hands the
utterance to command.py FIRST: the grammar fast path (session/dial/memory/
operator rows) answers locally in milliseconds with zero ring spend; only a
non-match falls to the brain ring with the persona prompt (LIVE dials, never
cached) plus a rolling <=10-message window. Every reply chunk/done pair ends
with the A2 done-shape: {chatId, messageId, hue, lane}. quick_action pays the
A1 debt (read_aloud/redo), A3 (enroll_voice), the ranked search pick, and the
P-CORE-8 'look' toggle ({} exactly, same engine as the grammar rows), and the
P-CORE-9 'status' chip ({} exactly, the same 5-line digest as the status row);
the RED-verb typed-YES seam is confirm(actionId, yes) per contract §3.
Since P-CORE-9 the boot also carries the §32 drill: send() confesses a dirty
prior run ONCE, first, mint LOCAL, speak queued — then never again. Since
P-CORE-10 the dialog serves A3's Living Brain explorer — list_brain(path) /
brain_text(path), read-only, path-confined, zero ring — and the standing
"stand down" close folds the day's journal + the ring-bounded sleep pass
(the kill-switch close folds nothing: Law 5 stays instant).

Design declarations (also pinned in code comments where they live):
- chunk.seq restarts per message until true streaming lands.
- Brain-call hue is 'cloud' by construction; local replies (acks) are 'local'.
- Remember-intents are honored for audience == "cooper" only; family/guest
  payloads fall through to a memory-less brain answer (command.py keeps the
  same fall-through, behavior byte-for-byte).
- The rolling history window rides ring calls for audience == "cooper" only
  (P-CORE-11 §31): under family/guest the window is empty by law — window
  rollover is luck, the matrix pins closure.
- The P-CORE-2 dial/remember handlers moved to command.py (harness moved,
  behavior untouched); classify_memory stays importable from here.
"""
from tars.core import canon, enroll, persona
from tars.core.clockd import Clockd
from tars.core.command import CommandLayer, classify_memory  # classify_memory: re-export, callers keep importing it from here
from tars.core.dailyops import NtOps
from tars.core.findfile import FileFinder, finder_roots_from_env
from tars.core.handover import FACTORY_KEY
from tars.core.logx import LogX
from tars.core.operator import NtExecutor
from tars.core.searchlanes import SearchLanes
from tars.core.telesend import TelethonUserClient
from tars.core.watcher import drill_boot, drill_mark_clean, survival_line

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
            clockd = Clockd(vault, bus)  # P-CORE-6: the durable clock, same vault, same bus
            command_layer = CommandLayer(settings, vault, NtExecutor(), SearchLanes(),
                                         FileFinder(finder_roots_from_env()),
                                         LogX(vault.path.parent / "logs.jsonl"), bus,
                                         router=router, clockd=clockd, ops=NtOps(),
                                         tele=TelethonUserClient(vault.path.parent))  # no secrets shelved: honestly unlinked
        self._command = command_layer
        self._clockd = command_layer.clockd_unit  # the layer's clock drives tick_clock's heartbeat
        self._chat_id = None
        # §32 power-cut drill: this run boots dirty (innocent only after a clean exit proves it);
        # a dirty PRIOR run returns the survival payload, spoken once on the first summon.
        self._survival = drill_boot(vault)
        bus.subscribe(lambda kind, _detail: drill_mark_clean(vault) if kind == "close" else None)

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
            self._speak_survival()  # §32: a power event is confessed ONCE, before anything else is answered
            if self._vault.kv_get(FACTORY_KEY) == "yes":  # Part IX: the wiped machine greets once
                self._vault.kv_set(FACTORY_KEY, "no")  # consumed before speaking — never twice
                if self._chat_id is None:
                    self.new_chat()  # the greeting persists into a real chat, never a null row
                self._emit_message(canon.LINE_FACTORY, "local", None)
        if self._chat_id is None:
            self.new_chat()
        self._machine.text()
        self.tick_clock()  # clock heartbeat: missed-while-OFF fires once, here, before the turn
        self._dispatch(str(text))
        return {"chatId": self._chat_id}

    def _speak_survival(self) -> None:
        """First summon after a dirty end: the survival report, mint and local, then consumed."""
        if self._survival is None:
            return
        payload, self._survival = self._survival, None  # consumed before speaking — never twice
        if self._chat_id is None:
            self.new_chat()
        line = survival_line(self._vault, payload["when"])
        mid = self._emit_message(line, "local", None)
        self._vault.kv_set(f"speak_request:{mid}", "queued")

    def send_voice(self, text) -> dict:
        """Voice entry: ears own capture + heard(); the dialog takes over from THINKING."""
        if self._machine.state != "thinking":
            return {"ok": False, "line": canon.LINE_CATCH_ALL}
        if self._chat_id is None:
            self.new_chat()
        self.tick_clock()  # same heartbeat on the voice door
        self._dispatch(str(text))
        return {"chatId": self._chat_id}

    def tick_clock(self, now_epoch=None) -> list:
        """Clock heartbeat (grammar v1.1 + v1.3): every due reminder/timer fires once as a
        persisted LOCAL assistant line and queues for the mouth via the A1 speak intake;
        the same tick drives the LOOK session — idle-off (mint) and narration (amber)
        lines persist with their own hues. The state machine dances only mid-turn."""
        fired = self._clockd.tick(now_epoch)
        lines = []
        if fired:
            if self._chat_id is None:
                self.new_chat()  # a fired line must persist into a real chat, never a null row
            mid_turn = self._machine.state == "thinking"
            if mid_turn:
                self._machine.reply()
            for detail in fired:
                mid = self._emit_message(detail["line"], "local", None)
                self._vault.kv_set(f"speak_request:{mid}", "queued")  # the mouth drains when a tier is live
            if mid_turn:
                self._machine.spoken()
            lines = [detail["line"] for detail in fired]
        # LOOK heartbeat (grammar v1.3): the same tick drives idle-off (mint) and narration
        # (amber) lines — each persisted with its own hue, each queued for the mouth.
        lookd = self._command.lookd_unit
        if lookd is not None:
            for text, hue, lane in lookd.tick(now_epoch):
                if self._chat_id is None:
                    self.new_chat()
                mid = self._emit_message(text, hue, lane)
                self._vault.kv_set(f"speak_request:{mid}", "queued")
                lines.append(text)
        # Handover heartbeat (Part IX): the standing tick observes the countdown deadline —
        # the wipe speaks nothing here; the factory line greets at the next summon.
        self._command.handover_unit.tick()
        return lines

    def _dispatch(self, text: str) -> None:
        self._machine.reply()
        if self._voice_gate is not None and self._voice_gate.try_passphrase(text, self._machine):
            self._emit_message(canon.LINE_VERIFIED, "local", None)
            self._machine.spoken()
            return  # §22: a correct pass restores Tier-1 — the pass text never persists, never routes
        user_mid = self._vault.message_add(self._chat_id, "cooper", text, None, None)
        plan = self._command.execute(str(text), self._machine, self._chat_id)
        if plan["handled"]:
            if plan["new_chat"]:
                self.new_chat()  # the boot line opens the FRESH chat; the command itself closed the old one
            emitted = []
            for line, hue, lane in plan["replies"]:
                emitted.append(self._emit_message(line, hue, lane))
            if plan.get("speak") is not None:  # P-CORE-12 row (32): the page's voice queues
                self._vault.kv_set(f"speak_request:{emitted[plan['speak']]}", "queued")
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

    _BRAIN_PERSONAL_SHELVES = ("people", "journal", "inner")  # §31: Cooper's alone (P-CORE-11)

    def _explorer_allowed(self, path: str) -> bool:
        """P-CORE-11 §7-1 hardening: the personal shelves gate by audience at the bridge too.
        The root listing stays open (shelf names are structural); people/journal/inner
        bytes and listings answer Cooper alone — the refusal carries zero content bytes."""
        if self._machine.audience == "cooper":
            return True
        parts = str(path or "").strip().replace("\\", "/").strip("/").split("/", 1)
        return parts[0] not in self._BRAIN_PERSONAL_SHELVES

    def list_brain(self, path: str = ""):
        """A3 (P-CORE-10, earned surface): the Living Brain explorer — read-only,
        path-confined. Success -> [BrainNode]; escape -> the clean refusal dict."""
        unit = self._command.brain_unit
        if unit is None:
            return {"ok": False, "line": canon.LINE_BRAIN_ABSENT}
        if not self._explorer_allowed(path):
            return {"ok": False, "line": canon.LINE_INNER_PRIVATE}
        return unit.list_brain(path)

    def brain_text(self, path: str):
        """A3: a leaf's preview bytes; escape/kind-mismatch/absent -> refusal dict. Zero ring."""
        unit = self._command.brain_unit
        if unit is None:
            return {"ok": False, "line": canon.LINE_BRAIN_ABSENT}
        if not self._explorer_allowed(path):
            return {"ok": False, "line": canon.LINE_INNER_PRIVATE}
        return unit.brain_text(path)

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
        if name == "look":  # P-CORE-8: contract-rostered chip — toggles the SAME engine the grammar rows drive
            if payload:  # the chip takes {} exactly (the enroll_voice law) — anything else never guesses
                return {"ok": False, "line": canon.LINE_CATCH_ALL}
            unit = self._command.lookd_unit
            line = unit.stop() if (unit and unit.watching) else (unit.start() if unit else canon.LINE_LOOK_NO_SEAM)
            if self._chat_id is None:
                self.new_chat()
            self._emit_message(line, "local", None)
            return {"ok": True, "line": line}
        if name == "status":  # P-CORE-9: rostered chip — serves the same digest as the status row
            if payload:
                return {"ok": False, "line": canon.LINE_CATCH_ALL}
            unit = self._command.watcher_unit
            line = unit.status_report() if unit else canon.LINE_CATCH_ALL
            if self._chat_id is None:
                self.new_chat()
            self._emit_message(line, "local", None)
            return {"ok": True, "line": line}
        if name == "council":  # P-CORE-12: rostered chip, SERVED — a named one-shot parliament
            question = str(payload.get("text", "")).strip() if isinstance(payload, dict) else ""
            if not question or set(payload) != {"text"}:  # the chip takes {text} exactly — never a guessed summon
                return {"ok": False, "line": canon.LINE_NEAR_MISS}  # zero ring, honest question
            if self._router is None:
                return {"ok": False, "line": canon.LINE_CATCH_ALL}
            reply = self._router.route(f"council on {question}", system_prompt=self._system_prompt())
            if self._chat_id is None:
                self.new_chat()
            for notice in reply["notices"]:
                self._emit_message(notice, "cloud", None)
            self._emit_message(reply["text"], "cloud", reply["lane"])  # response law: persist + stream
            return {"ok": reply["ok"], "line": reply["text"]}
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

    def _history_window(self, chat_id: int, before_mid: int) -> list:
        # Part IX §31: the rolling window is Cooper-era context — personal by charter, exactly
        # like the memories. Under family/guest watch the ring call rides stateless, or a prior
        # personal answer (or his own remembered line) would leak through the side window.
        if self._machine.audience != "cooper":
            return []
        return [{"role": ("user" if m["who"] == "cooper" else "assistant"), "content": m["text"]}
                for m in self._vault.message_context(chat_id, before_mid, CONTEXT_WINDOW)]

    def _brain_turn(self, text: str, user_mid: int) -> None:
        history = self._history_window(self._chat_id, user_mid)
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
        history = self._history_window(ids[0], user_message["id"])
        reply = self._router.route(user_message["text"], system_prompt=self._system_prompt(), history=history)
        notice_marks = 0
        for notice in reply["notices"]:
            self._emit_message(notice, "cloud", None)
            notice_marks += 1
        new_mid = self._emit_message(reply["text"], "cloud", reply["lane"])
        self._vault.message_mark_superseded(message["id"])  # after the insert: on a crash mid-redo we duplicate, never lose
        self._machine.spoken()
        return {"ok": True, "chatId": ids[0], "messageId": new_mid}
