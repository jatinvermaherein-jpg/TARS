"""The parse-before-brain fast path — command-grammar v1.0, row for row.

Parse order is canon and re-proven by the battery: (1) session/system ->
(2) dials -> (3) memory -> (4) named brain gates (router-owned; this file never
touches them) -> (5) operator GREEN -> (6) operator RED (typed-YES gate) ->
(7) study (P-CORE-12's — declared no-op fall-through) -> (8) else -> brain ring.

Match rules (grammar §0): case-insensitive, trimmed, WHOLE-UTTERANCE match,
numbers as digits or words 0–100, one command per utterance, closed alias
lists, nothing fuzzy ever. A grammar hit never touches the ring — the
battery proves zero adapter calls per hit. A near-miss earns ONE short
clarifying question and nothing executes. TARS never guesses targets (§16).

The §34 Never List scanner is the iron door: declared pattern table below,
byte-pinned from the bible; EVERY action target (green, red, search, find)
passes it. A hit answers LINE_NEVER_LIST — no gate, no exception path.
"""
import json
import re
import time
from datetime import datetime

from tars.core import canon, clockd, office, telesend
from tars.core.operator import APP_ALIASES

# --- moved here from dialog.py (P-CORE-2 handlers consolidated; behavior byte-identical)
DIAL_NAMES = ("humor", "vernacular", "discretion", "trust", "honesty")
REMEMBER_PATTERNS = ("remember this", "remember that", "note that", "yaad rakh")
PERSON_WORDS = ("ma", "papa", "bhaiya", "didi", "friend", "teacher", "sir", "uncle", "aunty")
PLAN_WORDS = ("plan", "tomorrow", "remind", "exam", "test", "deadline", "result")
PREFERENCE_WORDS = ("prefer", "prefers", "like", "likes", "love", "loves", "favorite", "favourite",
                    "hate", "hates", "dislike", "dislikes")

# Preset values per bible §10 (H/V only — discretion/trust are never preset-moved).
DIAL_PRESETS = {
    "recruit mode": {"humor": 5, "vernacular": 30},
    "docking mode": {"humor": 0, "vernacular": 0},
    "endurance mode": {"humor": 60, "vernacular": 60},
}

# Bible §34 (verbatim family): cracks · KMS · registry-Office tricks · driver boosters ·
# CCleaner-type cleaners · debloat scripts · real-actor voice clones · piracy · CAPTCHA/bot evasion.
NEVER_PATTERNS = (
    "crack", "cracks", "cracked", "keygen", "kms", "kmspico", "activator",
    "registry office", "office registry", "office activation", "windows activation",
    "driver booster", "driver-booster", "driverbooster", "ccleaner", "debloat",
    "voice clone", "voice-clone", "voiceclone",
    "piracy", "pirated", "pirate bay", "torrent", "crackwatch",
    "captcha", "bot evasion", "bot-evasion", "bypass bot",
)

NEAR_MISS_MARKERS = {
    "open", "close", "delete", "move", "volume", "brightness", "snap", "screenshot",
    "shutdown", "restart", "sleep", "search", "find", "dhundo", "kholo", "awaaz", "band",
    "remind", "alarm", "timer", "copy", "clipboard", "make", "write",  # grammar v1.1 families
    "send", "bhejo", "forward", "save", "forget",  # grammar v1.2 TeleSend family
}

RANK_WORDS = {"one": 1, "1": 1, "first": 1, "two": 2, "2": 2, "second": 2,
              "three": 3, "3": 3, "third": 3}

GATE_TTL_S = 120  # a parked RED verb expires fast; single-use, logged, never resurrected

COMMANDS_HELP = (
    "Commands, grouped:\n"
    "Session: stand down · cancel · yes (inside a gate) · new chat · status · commands · what time is it · what's the date\n"
    "Dials: humor/vernacular/discretion/trust 0-100 · presets recruit/docking/endurance · what are your dials\n"
    "Memory: remember this: ... · yaad rakh ... · what do you remember about ...\n"
    "Brain: council <question> · ultra <question>\n"
    "Operator: open <app> (kholo) · search <query> (on youtube) · find <desc> (dhundo) · volume (awaaz badha/ghata) · brightness · snap · screenshot\n"
    "Red, always typed-YES: close <app> · delete <file> · move <a> to <b> · shutdown · restart · sleep"
)

_RECALL_PREFIX = "what do you remember about "


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
    """'<dial> <digits-or-words>' -> (name, value), whole-utterance. The pinned P-CORE-2 shape:
    a 2-token bad number rides as None into the canon catch-all; a longer non-number tail is
    NOT the row (the layer's near-miss law answers those with one question, never the error line)."""
    parts = text.strip().lower().split()
    if len(parts) == 2 and parts[0] in DIAL_NAMES:
        return parts[0], canon.words_number(parts[1])
    if len(parts) == 3 and parts[0] in DIAL_NAMES:
        value = canon.words_number(" ".join(parts[1:]))
        if value is not None:  # two-word numbers 0..100: "sixty five", "one hundred"
            return parts[0], value
    return None


def remember_payload(text: str):
    """Declared pattern list (English + Hinglish basics). Empty payload -> normal chat."""
    lowered = text.strip().lower()
    for pattern in REMEMBER_PATTERNS:
        if lowered.startswith(pattern):
            payload = text.strip()[len(pattern):].lstrip(" :,-").strip()
            return payload or None
    return None


def never_list_hit(target: str) -> bool:
    """The §34 iron-door scan: every pattern matches on alnum boundaries (a punctuation
    neighbor is still a hit — 'crack.exe'; a letter-glued false-friend is not — 'marksmanship')."""
    padded = f" {' '.join(str(target).lower().split())} "
    for pattern in NEVER_PATTERNS:
        if re.search(rf"(?<![a-z0-9]){re.escape(pattern)}(?![a-z0-9])", padded):
            return True
    return False


class CommandLayer:
    """The parser + dispatcher. execute() returns a reply PLAN; the dialog persists and
    streams it. The layer owns no rendering — only intents, gates, and canon replies."""

    def __init__(self, settings, vault, executor, search_lanes, finder, log, bus, clock=None,
                 time_fn=None, router=None, clockd=None, ops=None, desktop=None, tele=None):
        self._settings = settings
        self._vault = vault
        self._executor = executor
        self._lanes = search_lanes
        self._finder = finder
        self._log = log
        self._bus = bus
        self._clock = clock or datetime.now
        self._time = time_fn or time.time
        self._router = router  # Office rows are the ONE ring-spending family (grammar v1.1, declared)
        self._clockd = clockd
        self._ops = ops
        self._desktop = desktop or office.desktop_dir()
        self._tele = tele  # P-CORE-7: the outbound client (real on the AiO, fixture in tests)

    @property
    def clockd_unit(self):
        """The clock the dialog heartbeats (owned here so both share one vault+bus binding)."""
        return self._clockd

    # ---------- gates (RED verbs) ----------

    def _park(self, action: tuple, summary: str, target: str, kind: str = "red-verb") -> str:
        # P-CORE-7: TeleSend reuses this exact machinery (single-use, 120s TTL, cancel-consumes)
        # — only the contract action-kind label differs ("telesend"); zero forked gate code.
        seq = int(self._vault.kv_get("gate:seq") or 0) + 1
        self._vault.kv_set("gate:seq", str(seq))
        action_id = f"act-{seq}"
        record = {"action": list(action), "summary": summary, "target": target, "created": self._time()}
        self._vault.kv_set(f"gate:{action_id}", json.dumps(record))
        self._vault.kv_set("gate:pending", action_id)
        self._bus.emit("action", {"actionId": action_id, "kind": kind, "summary": summary, "target": target})
        self._log.entry("gate", id=action_id, state="parked", target=target)
        return summary

    def confirm(self, action_id: str, yes: bool = False) -> dict:
        """Typed-YES seam: releases a parked verb exactly once. Unknown/expired/consumed
        ids answer LINE_CANCEL — a YES never guesses what it confirms."""
        raw = self._vault.kv_get(f"gate:{action_id}")
        if raw is None or raw in ("consumed", "expired"):
            return {"ok": False, "line": canon.LINE_CANCEL}
        record = json.loads(raw)
        if self._time() - record["created"] > GATE_TTL_S:
            self._vault.kv_set(f"gate:{action_id}", "expired")
            if self._vault.kv_get("gate:pending") == action_id:
                self._vault.kv_set("gate:pending", "")
            self._log.entry("gate", id=action_id, state="expired")
            return {"ok": False, "line": canon.LINE_CANCEL}
        self._vault.kv_set(f"gate:{action_id}", "consumed")  # single-use, always
        if self._vault.kv_get("gate:pending") == action_id:
            self._vault.kv_set("gate:pending", "")
        if not yes:
            self._log.entry("gate", id=action_id, state="cancelled")
            return {"ok": True, "line": canon.LINE_CANCEL}
        verb = record["action"]
        performed = self._run_action(verb)
        self._log.entry("gate", id=action_id, state="executed" if performed else "executor-refused",
                        target=record["target"])
        return {"ok": performed, "line": self._action_line(verb, performed, record["target"])}

    def _run_action(self, verb: list) -> bool:
        name = verb[0]
        if name == "close_app":
            return self._executor.close_app(verb[1])
        if name == "delete_path":
            return self._executor.delete_path(verb[1])
        if name == "move_path":
            return self._executor.move_path(verb[1], verb[2])
        if name == "tele_text":
            return self._deliver("telegram", "text", verb[1], verb[2], verb[3])
        if name == "tele_file":
            return self._deliver("telegram", "file", verb[1], verb[2], verb[3])
        if name == "wa_text":
            return self._deliver("whatsapp", "text", verb[1], verb[2], verb[3])
        return self._executor.power(verb[1], verb[2])

    def _deliver(self, channel: str, kind: str, key: str, display: str, payload: str) -> bool:
        """The YES release for TeleSend: re-resolve the contact FRESH (a 120s gate can outlive
        a book edit), touch the wire exactly once, and journal SUCCESS ONLY — the sent ledger
        records what left the box, never the intent."""
        contact = self._vault.contact_get(key)
        if contact is None:
            return False
        if channel == "telegram":
            handle = contact["telegram"]
            if not handle or self._tele is None or not self._tele.linked():
                return False
            ok = (self._tele.send_text(handle, payload) if kind == "text"
                  else self._tele.send_document(handle, payload))
        else:
            number = contact["whatsapp"]
            if not number:
                return False
            ok = bool(self._executor.open_url(telesend.wa_url(number, payload)))  # door opened; the thumb sends
        self._log.entry("telesend", channel=channel, family=kind, to=display, ok=ok)
        if ok:
            self._vault.sent_add(channel, display, kind, payload, self._time())
        return ok

    def _action_line(self, verb: list, performed: bool, target: str) -> str:
        if verb[0] == "tele_text" or verb[0] == "tele_file":
            return canon.sent_ack(verb[2], "Telegram") if performed else canon.LINE_TELE_FAILED
        if verb[0] == "wa_text":
            return canon.opened_ack(verb[2]) if performed else canon.LINE_TELE_FAILED
        if not performed:
            return f"The {target} action could not be completed from here."
        if verb[0] == "close_app":
            return canon.close_ack(verb[1])
        if verb[0] == "delete_path":
            return canon.delete_ack(verb[1])
        if verb[0] == "move_path":
            return canon.move_ack(verb[1], verb[2])
        return canon.power_ack(verb[1], verb[2])

    def open_rank(self, rank):
        """'open the second': resolve against the last search's pinned rows; None = never a guess."""
        raw = self._vault.kv_get("search:last")
        if raw is None:
            return None
        rows = json.loads(raw).get("rows", [])
        if not isinstance(rank, int) or rank < 1 or rank > len(rows):
            return None
        row = rows[rank - 1]
        self._executor.open_url(row["url"])
        self._log.entry("search-pick", rank=rank, title=row["title"])
        return {"rank": rank, "title": row["title"], "url": row["url"],
                "line": canon.open_rank_line(rank, row["title"])}

    # ---------- the parser ----------

    def execute(self, text: str, machine, chat_id=None) -> dict:
        """-> {"handled": True, "replies": [(line, hue, lane)], ...flags} or {"handled": False}.
        Only replies are returned; emitting is the dialog's uniform-response law."""
        raw = str(text)  # remember payload bytes persist original-case (P-CORE-2 law): match on t, slice raw
        t = " ".join(raw.strip().lower().split())
        # rn = whitespace-normalized raw, ORIGINAL case, index-aligned with t (P-CORE-7 law:
        # an outbound payload is staged as Cooper typed it — §17 exact bytes)
        rn = " ".join(raw.strip().split())

        # (1) session / system
        if t == "stand down":
            return self._plan([(canon.LINE_EXIT, "local", None)], stand_down=True)
        if t == "cancel":
            pending = self._vault.kv_get("gate:pending")
            if pending:  # abort CONSUMES the gate: a later confirm(id) can never resurrect it (§16)
                self._vault.kv_set(f"gate:{pending}", "consumed")
                self._vault.kv_set("gate:pending", "")
                self._log.entry("gate", id=pending, state="cancelled")
            return self._plan([(canon.LINE_CANCEL, "local", None)])
        if t == "yes" and self._vault.kv_get("gate:pending"):
            result = self.confirm(self._vault.kv_get("gate:pending"), yes=True)
            return self._plan([(result["line"], "local", None)])
        if t == "new chat":
            dials = self._settings.dials
            return self._plan([(canon.boot_line(dials["humor"], dials["vernacular"]), "local", None)], new_chat=True)
        if t in ("status", "system status"):
            return self._plan([(canon.pending_line("The Watcher report", "P-CORE-9"), "local", None)])
        if t in ("commands", "help"):
            return self._plan([(COMMANDS_HELP, "local", None)])
        if t in ("what time is it", "what is the time"):
            return self._plan([(canon.time_line(self._clock()), "local", None)])
        if t in ("what's the date", "what is the date"):
            return self._plan([(canon.date_line(self._clock()), "local", None)])

        # (2) dials (moved P-CORE-2 handler, behavior byte-identical)
        dial = parse_dial_command(t)
        if dial is not None:
            return self._plan([(self._dial_line(machine, *dial), "local", None)])
        if t.split() and t.split()[0] in DIAL_NAMES:
            return self._plan([(canon.LINE_NEAR_MISS, "local", None)])  # dial-first, not the row: one question
        if t in DIAL_PRESETS:
            return self._plan(self._preset_lines(machine, t))
        if t == "what are your dials":
            return self._plan([(canon.dials_line(self._settings.dials), "local", None)])

        # (3) memory (moved P-CORE-2 handler, behavior byte-identical)
        payload = remember_payload(raw)
        if payload is not None and machine.audience == "cooper":
            self._vault.remember(classify_memory(payload), payload)
            return self._plan([(canon.LINE_NOTED, "local", None)])
        if t.startswith(_RECALL_PREFIX) and machine.audience == "cooper":
            needle = t[len(_RECALL_PREFIX):].strip()
            if needle:
                hits = [row["text"] for row in self._vault.recall() if needle in row["text"].lower()]
                if hits:
                    listing = "What I remember about that:\n" + "\n".join(f"{i + 1}. {h}" for i, h in enumerate(hits))
                    return self._plan([(listing, "local", None)])
                return self._plan([(canon.LINE_NOTHING_REMEMBERED, "local", None)])

        # (4) named brain gates — router-owned (council/ultra prefixes never parse as commands)
        if t.startswith("council") or t.startswith("ultra"):
            return {"handled": False}

        # (5) operator GREEN
        green = self._green(t)
        if green is not None:
            return green

        # (5b) daily ops (grammar v1.1: clock rows, clipboard, Office Studio)
        daily = self._daily(t, chat_id)
        if daily is not None:
            return daily

        # (5c) TeleSend (grammar v1.2: people-book, send rows, sent recall)
        teleplan = self._tele_rows(rn, t)
        if teleplan is not None:
            return teleplan

        # (6) operator RED — the typed-YES gate
        red = self._red(t)
        if red is not None:
            return red

        # (7) study rows are P-CORE-12's: declared no-op fall-through — the ring answers for now

        # near-miss law (grammar §0): HIGH STRUCTURE = a command verb opens the utterance but no
        # exact row matched -> ONE clarifying question, nothing moves. Keyword-anywhere would be
        # substring fishing (banned) and would steal plain conversation from the ring.
        if t and t.split(" ", 1)[0] in NEAR_MISS_MARKERS:
            return self._plan([(canon.LINE_NEAR_MISS, "local", None)])

        # (8) else: the brain ring is conversation's home
        return {"handled": False}

    def _plan(self, replies, stand_down=False, new_chat=False) -> dict:
        return {"handled": True, "replies": replies, "stand_down": stand_down, "new_chat": new_chat}

    def _dial_line(self, machine, name, value) -> str:
        if machine.audience != "cooper":
            return canon.LINE_GUEST_DIAL  # §10: only Cooper's verified voice or the panel moves dials
        result = self._settings.set_dial(name, value)
        if result["ok"]:
            machine.emit_notice()  # dials move live mid-conversation: fresh StateNotice
        return result["line"]

    def _preset_lines(self, machine, name) -> list:
        if machine.audience != "cooper":
            return [(canon.LINE_GUEST_DIAL, "local", None)]
        moved = []
        for dial in ("humor", "vernacular"):  # bible §10: presets define H/V only, in order
            target = DIAL_PRESETS[name][dial]
            if self._settings.dials[dial] != target:
                result = self._settings.set_dial(dial, target)
                moved.append((result["line"], "local", None))
        if moved:
            machine.emit_notice()
            return moved
        dials = self._settings.dials
        return [(canon.preset_idle_line(name, dials["humor"], dials["vernacular"]), "local", None)]

    def _never(self, target: str) -> bool:
        """One scan site for every action target: hit -> LINE_NEVER_LIST, logged, no execution."""
        if never_list_hit(target):
            self._log.entry("never-list", target=target)
            return True
        return False

    def _green(self, t: str):
        # ranked pick: "open one" / "open the second" / "open 2"
        if t.startswith("open "):
            tail = t[5:].split()
            tail = [w for w in tail if w not in ("the", "result")]
            if len(tail) == 1 and tail[0] in RANK_WORDS:
                picked = self.open_rank(RANK_WORDS[tail[0]])
                if picked is None:
                    return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
                return self._plan([(picked["line"], "cloud", None)])

        # open <app> — aliases closed; Hinglish kholo rows
        opened = self._alias_after(t, "open ", "kholo ", " kholo")
        if opened is not None:
            alias, display_launch = opened
            if self._never(display_launch):  # §34 outranks ambiguity: a banned target is never clarified into a launch
                return self._plan([(canon.LINE_NEVER_LIST, "local", None)])
            if alias is None:
                return self._plan([(canon.clarify_app_line(display_launch), "local", None)])
            display, launch = APP_ALIASES[alias]
            if self._executor.open_app(launch):
                return self._plan([(canon.open_ack(display), "local", None)])
            return self._plan([(canon.open_fail_ack(display), "local", None)])

        # search lanes (grammar §5): "search <q> on youtube" / "search <q>"
        if t.startswith("search "):
            body = t[len("search "):].strip()
            if body:
                on_youtube = body.endswith(" on youtube")
                query = body[:-len(" on youtube")].strip() if on_youtube else body
                if self._never(query):
                    return self._plan([(canon.LINE_NEVER_LIST, "local", None)])
                rows = self._lanes.youtube(query) if on_youtube else self._lanes.web(query)
                if not rows:
                    return self._plan([(canon.LINE_NO_RESULTS, "cloud", None)])
                self._vault.kv_set("search:last", json.dumps(
                    {"lane": "youtube" if on_youtube else "web", "query": query, "rows": rows}))
                listing = "\n".join(canon.search_row_line(r["rank"], r["title"], r["source"]) for r in rows)
                return self._plan([(listing + "\n" + canon.search_picks_line(), "cloud", None)])

        # find <desc> — natural find, honest lists
        found = self._strip_any(t, ("find ", "dhundo "), (" dhundo",))
        if found is not None and found:
            if self._never(found):
                return self._plan([(canon.LINE_NEVER_LIST, "local", None)])
            outcome, payload = self._finder.find(found)
            if outcome == "single":
                return self._plan([(canon.find_one_line(payload), "local", None)])
            if outcome == "list":
                return self._plan([(canon.find_list_line(payload), "local", None)])
            return self._plan([(canon.LINE_FIND_NONE, "local", None)])

        # volume / brightness / snap / screenshot (declared system verbs + Hinglish awaaz rows)
        volume_rows = {"volume up": ("up", self._executor.volume_up), "volume down": ("down", self._executor.volume_down),
                       "volume mute": ("mute", self._executor.volume_mute), "awaaz badha": ("up", self._executor.volume_up),
                       "awaaz ghata": ("down", self._executor.volume_down)}
        if t in volume_rows:
            action, call = volume_rows[t]
            call()
            return self._plan([(canon.volume_ack(action), "local", None)])
        if t.startswith("volume set "):
            level = canon.words_number(t[len("volume set "):])
            if level is None:
                return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
            self._executor.volume_set(level)
            return self._plan([(canon.volume_ack("set", level), "local", None)])
        brightness_rows = {"brightness up": ("up", self._executor.brightness_up),
                           "brightness down": ("down", self._executor.brightness_down)}
        if t in brightness_rows:
            action, call = brightness_rows[t]
            call()
            return self._plan([(canon.brightness_ack(action), "local", None)])
        if t.startswith("brightness set "):
            level = canon.words_number(t[len("brightness set "):])
            if level is None:
                return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
            self._executor.brightness_set(level)
            return self._plan([(canon.brightness_ack("set", level), "local", None)])
        snap_rows = {"snap left": ("left", self._executor.snap_left), "snap right": ("right", self._executor.snap_right),
                     "snap maximize": ("maximize", self._executor.snap_maximize)}
        if t in snap_rows:
            action, call = snap_rows[t]
            call()
            return self._plan([(canon.snap_ack(action), "local", None)])
        if t in ("screenshot", "screenshot full", "screenshot region"):
            # P-CORE-6 owns this row now: real capture on the AiO (BitBlt), the honest
            # unavailable line anywhere else — never a faked shot.
            kind = "region" if t == "screenshot region" else "full"
            if self._ops.screenshot(kind, self._desktop):
                return self._plan([(canon.LINE_SHOT_SAVED, "local", None)])
            return self._plan([(canon.meter_unavailable_line("Screenshot capture"), "local", None)])

        # system answers (grammar v1.1): readings or the canon unavailable line — never a guess
        if t == "uptime":
            seconds = self._ops.uptime_seconds()
            if seconds is False:
                return self._plan([(canon.meter_unavailable_line("The uptime meter"), "local", None)])
            return self._plan([(canon.uptime_ack(int(seconds // 3600)), "local", None)])
        if t == "ram":
            percent = self._ops.ram_percent()
            if percent is False:
                return self._plan([(canon.meter_unavailable_line("The RAM meter"), "local", None)])
            return self._plan([(canon.ram_ack(percent), "local", None)])
        if t == "storage":
            try:
                free_gb = self._ops.storage_free_bytes("/") // (1024 ** 3)
            except (OSError, TypeError):
                return self._plan([(canon.meter_unavailable_line("The storage meter"), "local", None)])
            return self._plan([(canon.storage_ack(int(free_gb)), "local", None)])
        if t in ("cpu", "what's eating the cpu"):
            hog = self._ops.cpu_hog()
            if not hog:
                return self._plan([(canon.LINE_NO_CPU_METER, "local", None)])
            return self._plan([(canon.hog_ack(hog[0], hog[1]), "local", None)])
        return None

    # ---------- daily-ops rows (grammar v1.1) ----------

    def _daily(self, t: str, chat_id):
        now = self._clock()

        # reminders: "remind me to <text> <when>" · Hinglish "yaad dilana <text> <when>"
        remind_body = self._strip_any(t, ("remind me to ", "yaad dilana "), ())
        if remind_body:
            parsed = clockd.parse_reminder(remind_body, now)
            if parsed is None:
                return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
            text, epoch, echo = parsed
            rid = self._vault.reminder_insert(text, epoch, "", "reminder")
            self._log.entry("clock", row="reminder", id=rid, text=text)
            return self._plan([(canon.reminder_ack(text, echo), "local", None)])

        # alarms: "set an alarm for <when>" · "alarm lagao <when>"
        alarm_body = self._strip_any(t, ("set an alarm for ", "alarm lagao "), ())
        if alarm_body:
            parsed = clockd.parse_alarm(alarm_body, now)
            if parsed is None:
                return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
            epoch, echo = parsed
            rid = self._vault.reminder_insert("", epoch, "", "alarm")
            self._log.entry("clock", row="alarm", id=rid)
            return self._plan([(canon.alarm_ack(echo), "local", None)])

        # timers: "set a timer for N <units>" · "set a <label> timer for N <units>" · "timer lagao N <units>"
        timer_body = None
        if t.startswith("set a ") and " timer for " in t:
            timer_body = t[len("set a "):]
        elif t.startswith("timer lagao "):
            timer_body = t[len("timer lagao "):]
        if timer_body is not None and timer_body:
            parsed = clockd.parse_timer(timer_body, now)
            if parsed is None:
                return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
            label, epoch, echo = parsed
            tid = self._vault.timer_insert(label, epoch)
            self._log.entry("clock", row="timer", id=tid, label=label)
            return self._plan([(canon.timer_set_ack(label, echo), "local", None)])

        # "cancel the timer" / "cancel the alarm" — the NEXT-to-fire of that kind, never a guess
        if t == "cancel the timer":
            pending = self._vault.next_pending_timer()
            if pending is None:
                return self._plan([(canon.LINE_CANCEL, "local", None)])
            self._vault.timer_done(pending["id"])
            self._log.entry("clock", row="timer-cancel", id=pending["id"])
            target = f"the {pending['label']} timer" if pending["label"] else "the timer"
            return self._plan([(canon.cancel_ack(target), "local", None)])
        if t in ("cancel the alarm", "cancel the reminder"):
            pending = self._vault.next_pending_reminder("alarm" if t == "cancel the alarm" else "reminder")
            if pending is None:
                return self._plan([(canon.LINE_CANCEL, "local", None)])
            self._vault.reminder_done(pending["id"])
            self._log.entry("clock", row=f"{pending['kind']}-cancel", id=pending["id"])
            return self._plan([(canon.cancel_ack(f"the {pending['kind']}"), "local", None)])

        # clipboard rows (grammar v1.1): LOCAL read/write — the content never travels (§27/§31)
        if t == "copy that":
            last = self._vault.last_tars_text(chat_id)
            if last is None:
                return self._plan([(canon.LINE_NOTHING_TO_COPY, "local", None)])
            self._ops.clipboard_set(last)
            return self._plan([(canon.LINE_COPIED, "local", None)])
        if t == "what's on my clipboard":
            content = self._ops.clipboard_get()
            if not content:
                return self._plan([(canon.LINE_CLIPBOARD_EMPTY, "local", None)])
            return self._plan([(canon.clipboard_line(content), "local", None)])

        # Office Studio rows (grammar v1.1): the ONE ring-spending command family — the draft
        # travels (cloud hue + lane), the build is local (§18 Desktop, saved-line mint).
        office_row = self._strip_any(t, ("make a ppt on ", "write a doc on ", "write a document on "), ())
        if office_row is not None:
            kind = "pptx" if t.startswith("make a ppt on ") else "docx"
            topic = office_row
            if not topic:
                return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
            if self._never(topic):
                return self._plan([(canon.LINE_NEVER_LIST, "local", None)])
            reply = self._router.route(office.office_prompt(kind, topic))
            notices = [(note, "cloud", None) for note in reply["notices"]]  # ring courtesy lines always render
            if not reply["ok"]:
                return self._plan(notices + [(reply["text"], "cloud", reply["lane"])])
            parsed = office.parse_outline(kind, reply["text"])
            if parsed is None:
                return self._plan([(canon.LINE_CATCH_ALL, "cloud", reply["lane"])])
            title, payload = parsed
            if kind == "pptx":
                name = office.build_pptx(title, payload, self._desktop)
                draft = canon.office_draft_line(len(payload), "slides", title)
            else:
                name = office.build_docx(title, payload, self._desktop)
                draft = canon.office_draft_line(len(payload), "paragraphs", title)
            self._log.entry("office", family=kind, name=name, topic=topic)
            return self._plan(notices + [(draft, "cloud", reply["lane"]),
                                         (canon.saved_ack(name), "local", None)])
        return None

    # ---------- TeleSend rows (grammar v1.2) ----------

    _CHANNEL_SUFFIXES = ((" on telegram", "telegram", "Telegram"), (" on whatsapp", "whatsapp", "WhatsApp"))

    def _tele_rows(self, rn: str, t: str):
        """§17 in rows: every send is stage -> show -> YES. rn carries the original case
        (index-aligned with t); matching happens on t, payloads are sliced from rn."""

        # people-book: "save <name>'s telegram as <handle>" / "... whatsapp as <number>"
        if t.startswith("save ") and " as " in t:
            head_t = t[len("save "):].rsplit(" as ", 1)[0]
            tail_r = rn[len("save "):]
            head_r = tail_r.rsplit(" as ", 1)[0]
            value = tail_r.rsplit(" as ", 1)[1].strip()
            for marker, channel in (("'s telegram", "telegram"), ("'s whatsapp", "whatsapp")):
                if head_t.endswith(marker):
                    display = head_r[:-len(marker)].strip()
                    if not display or not value:
                        return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
                    status, row = self._vault.contact_save(display, channel, value)
                    channel_title = {"telegram": "Telegram", "whatsapp": "WhatsApp"}[channel]
                    self._log.entry("people-book", action=status, channel=channel, name=row["name"])
                    if status == "created":
                        return self._plan([(canon.contact_saved_ack(row["name"], channel_title), "local", None)])
                    if status == "filled":
                        return self._plan([(canon.contact_updated_ack(row["name"], channel_title), "local", None)])
                    return self._plan([(canon.contact_dup_line(row["name"], channel_title), "local", None)])

        # "forget <name>" — a true delete from the book, with the honest empty-book line
        if t.startswith("forget ") and t[len("forget "):].strip():
            removed = self._vault.contact_remove(t[len("forget "):].strip())
            if removed is None:
                return self._plan([(canon.no_contact_line(t[len("forget "):].strip()), "local", None)])
            self._log.entry("people-book", action="forgot", name=removed["name"])
            return self._plan([(canon.contact_forgot_ack(removed["name"]), "local", None)])

        # "who do i know" — honest numbered list, newest-first
        if t == "who do i know":
            rows = self._vault.contacts_list()
            if not rows:
                return self._plan([(canon.LINE_NO_CONTACTS, "local", None)])
            return self._plan([(canon.contacts_line(rows), "local", None)])

        # sent recall: "what did i send <name>" — the ledger speaks, capped per finder-law
        if t.startswith("what did i send "):
            key = t[len("what did i send "):].strip()
            if not key:
                return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
            rows = self._vault.sent_recall(key, limit=5)
            if not rows:
                return self._plan([(canon.nothing_sent_line(key), "local", None)])
            return self._plan([(canon.sent_recall_line(rows[0]["recipient"], rows), "local", None)])

        # file rows BEFORE generic text (they share the 'send' head): "forward <desc> to <name>
        # on <channel>" · "send (the) file <desc> to <name> on <channel>" — channel is required
        for prefix in ("send the file ", "send file ", "forward "):
            if t.startswith(prefix):
                return self._tele_file_row(rn, t, prefix)

        # text rows: "send <payload> to <name> on <channel>" (verbatim, ZERO ring) ·
        # "send <ask> to <name>" with no channel = the ONE lawful ring draft (smart lane,
        # staged on the Telegram user lane) · closed Hinglish alias: bhejo
        for prefix in ("send ", "bhejo "):
            if t.startswith(prefix) and " to " in t[len(prefix):]:
                return self._tele_text_row(rn, t, prefix)
        return None

    def _split_to_channel(self, body_t: str, body_r: str):
        """'<payload> to <name>[ on <channel>]' -> (payload_r, name_r, channel_key, channel_title).
        Closed rule: the FIRST ' to ' separates; the channel is a declared suffix only."""
        payload_t, rest = body_t.split(" to ", 1)
        payload_r = body_r[:len(payload_t)].strip()
        name_t = rest.strip()
        name_r = body_r.split(" to ", 1)[1].strip()
        for suffix, key, title in self._CHANNEL_SUFFIXES:
            if name_t.endswith(suffix):
                return payload_r, name_r[:-len(suffix)].strip(), key, title
        return payload_r, name_r, None, None

    def _contact_or_line(self, name_r: str, channel_title: str):
        """Resolve, then the pre-ring/pre-gate honesty ladder: unknown -> no_contact; known but
        the channel column is empty -> no_channel. Returns (contact, display, plan|None)."""
        contact = self._vault.contact_get(name_r)
        if contact is None:
            return None, name_r, self._plan([(canon.no_contact_line(name_r), "local", None)])
        display = contact["name"]
        if channel_title == "Telegram" and not contact["telegram"]:
            return None, display, self._plan([(canon.no_channel_line(display, channel_title), "local", None)])
        if channel_title == "WhatsApp" and not contact["whatsapp"]:
            return None, display, self._plan([(canon.no_channel_line(display, channel_title), "local", None)])
        return contact, display, None

    def _tele_text_row(self, rn: str, t: str, prefix: str):
        body_t, body_r = t[len(prefix):], rn[len(prefix):]
        payload, name_r, channel, channel_title = self._split_to_channel(body_t, body_r)
        if not payload or not name_r:
            return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
        if self._never(payload) or self._never(name_r):  # §34 scans BOTH the bytes and the target
            return self._plan([(canon.LINE_NEVER_LIST, "local", None)])
        if channel is None:  # the declared DRAFT row: one smart-lane spend, staged on Telegram
            contact, display, plan = self._contact_or_line(name_r, "Telegram")
            if plan is not None:
                return plan
            if not self._tele or not self._tele.linked():
                return self._plan([(canon.LINE_TELE_NOT_LINKED, "local", None)])
            reply = self._router.route(telesend.draft_prompt(payload, display))
            notices = [(note, "cloud", None) for note in reply["notices"]]
            if not reply["ok"]:
                return self._plan(notices + [(reply["text"], "cloud", reply["lane"])])
            drafted = reply["text"].strip()
            summary = self._park(("tele_text", display.lower(), display, drafted),
                                 canon.stage_text_line(display, "Telegram", drafted), display,
                                 kind="telesend")
            return self._plan(notices + [(canon.send_draft_line(drafted), "cloud", reply["lane"]),
                                         (summary, "local", None)])
        contact, display, plan = self._contact_or_line(name_r, channel_title)
        if plan is not None:
            return plan
        if channel == "telegram":
            if not self._tele or not self._tele.linked():
                return self._plan([(canon.LINE_TELE_NOT_LINKED, "local", None)])
            verb = "tele_text"
        else:
            verb = "wa_text"
        summary = self._park((verb, display.lower(), display, payload),
                             canon.stage_text_line(display, channel_title, payload), display,
                             kind="telesend")
        return self._plan([(summary, "local", None)])

    def _tele_file_row(self, rn: str, t: str, prefix: str):
        body_t, body_r = t[len(prefix):], rn[len(prefix):]
        if " to " not in body_t:
            return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
        desc, name_r, channel, channel_title = self._split_to_channel(body_t, body_r)
        if not desc or not name_r or channel is None:
            return self._plan([(canon.LINE_NEAR_MISS, "local", None)])
        if self._never(desc) or self._never(name_r):
            return self._plan([(canon.LINE_NEVER_LIST, "local", None)])
        if channel == "whatsapp":  # a ROW, not a boundary: the canon line, no staging (decree)
            return self._plan([(canon.LINE_WA_FILES_OFF, "local", None)])
        contact, display, plan = self._contact_or_line(name_r, "Telegram")
        if plan is not None:
            return plan
        if not self._tele or not self._tele.linked():
            return self._plan([(canon.LINE_TELE_NOT_LINKED, "local", None)])
        outcome, payload = self._finder.find(desc)
        if outcome == "list":
            return self._plan([(canon.find_list_line(payload), "local", None)])
        if outcome == "none":
            return self._plan([(canon.LINE_FIND_NONE, "local", None)])
        # File bytes never enter a ring payload; the staged artifact is a PATH (full, shown).
        summary = self._park(("tele_file", display.lower(), display, payload),
                             canon.stage_file_line(display, payload), display, kind="telesend")
        return self._plan([(summary, "local", None)])

    def _red(self, t: str):
        # close <app> — always gated (band karo alias rows included)
        closed = self._alias_after(t, "close ", "band karo ", " band karo")
        if closed is not None:
            alias, display_token = closed
            if self._never(display_token):  # §34 outranks ambiguity: a banned target is never clarified into a gate
                return self._plan([(canon.LINE_NEVER_LIST, "local", None)])
            if alias is None:
                return self._plan([(canon.clarify_app_line(display_token), "local", None)])
            display = APP_ALIASES[alias][0]
            summary = self._park(("close_app", display), canon.confirm_line(display, "closes"), display)
            return self._plan([(summary, "local", None)])

        if t.startswith("delete "):
            target = t[len("delete "):].strip()
            if target:
                if self._never(target):
                    return self._plan([(canon.LINE_NEVER_LIST, "local", None)])
                summary = self._park(("delete_path", target), canon.confirm_line(target), target)
                return self._plan([(summary, "local", None)])

        if t.startswith("move ") and " to " in t:
            body = t[len("move "):]
            source, dest = (part.strip() for part in body.split(" to ", 1))
            if source and dest:
                if self._never(source) or self._never(dest):
                    return self._plan([(canon.LINE_NEVER_LIST, "local", None)])
                target = f"{source} to {dest}"
                summary = self._park(("move_path", source, dest), canon.confirm_line(target, "moves"), target)
                return self._plan([(summary, "local", None)])

        power_verbs = {"shutdown": ("shutdown", "shuts down"), "restart": ("restart", "restarts"),
                       "sleep": ("sleep", "sleeps")}
        if t in power_verbs:
            verb, phrase = power_verbs[t]
            summary = self._park(("power", verb, 30),
                                 canon.confirm_line("the PC in thirty seconds", phrase), "this PC")
            return self._plan([(summary, "local", None)])
        return None

    def _alias_after(self, t: str, prefix_en: str, prefix_hi: str, suffix_hi: str):
        """'<verb> <alias>' with the declared Hinglish shapes -> (alias_key|None, token)."""
        rest = None
        if prefix_en and t.startswith(prefix_en):
            rest = t[len(prefix_en):].strip()
        elif prefix_hi and t.startswith(prefix_hi):
            rest = t[len(prefix_hi):].strip()
        elif suffix_hi and t.endswith(suffix_hi):
            rest = t[:-len(suffix_hi)].strip()
        if rest is None or not rest:
            return None
        if rest in APP_ALIASES:
            return rest, rest
        return None, rest

    def _strip_any(self, t: str, prefixes: tuple, suffixes: tuple):
        for prefix in prefixes:
            if t.startswith(prefix):
                return t[len(prefix):].strip()
        for suffix in suffixes:
            if t.endswith(suffix):
                return t[:-len(suffix)].strip()
        return None
