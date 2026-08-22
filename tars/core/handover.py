"""The Handover (Part IX — the built-in farewell).

The last thing TARS does for Cooper is leave cleanly. The doctrines, all
battery-pinned:

THE TRIPLE GATE + WINDOW — verified Cooper tier (the standing audience
truth: family/guest hear LINE_HANDOVER_VOICE_ONLY and no flow starts) ->
the spoken passphrase verified through the STANDING hash flow
(pass_credentials + hash_passphrase from voiceid.py — reused, never
forked) -> typed CONFIRM -> the keys question (Part IX's ask: YES keeps
them, anything-else-law applies at every gated stage: an utterance that
isn't the answer cancels honestly) -> a 10-second ABORTABLE countdown.
"abort handover" / "cancel" inside the window stops it cold, everything
stays. Other conversation flows NORMALLY during the window (the countdown
never hijacks the desk). Completion alone triggers the wipe; the deadline
is observed at the standing tick seam (the app heartbeats per second; the
battery drives tick directly).

LAW 5 — any close event (kill-switch above all) while the flow is alive
kills the flow INSTANTLY and NOTHING is wiped. A countdown never survives
process death: a crashed countdown is a dead countdown on reopen, never a
resumed one.

THE WIPE (§30 ledger, ordered, per-store atomic — each store lands wholly
pre or wholly post): 1 vault rows (ONE sqlite transaction — schema stands)
· 2 profiles.json (fresh empty Member File, atomic replace) · 3
settings.json (factory dials; honesty 90 never moved) · 4 the secrets
mapping (only when disowned: caller-provided in the sandbox; the AiO-era
file erase is nt truth — canon comment) · 5 tars-brain/ in full (line-230
law: the mind dies with its commander; the shelves re-grow empty at the
next brain construction) · 6 logs.jsonl — every personal line purged,
EXACTLY ONE survives: `Handover executed <date>` (a valid logx entry whose
raw bytes carry the phrase + an ISO date — the parse-back law holds).

KEPT — house rules aren't memories: the app, canon, the laws, the Never
List, grammar/bible semantics, the gauge/ring SCHEMAS. Windows + user
files are 100% outside the blast radius: the wipe's write set is exactly
{vault rows, profiles.json, settings.json, logs.jsonl, tars-brain/, the
in-memory secrets mapping when disowned} — the battery negative-space pin
asserts a sentinel user tree survives byte-for-byte.

IRREVERSIBILITY — there is deliberately NO copy, NO shadow, NO undo seam
anywhere in this module (grep-pinned): a wipe that secretly remembers is
a lie with extra steps.

AFTER — the vault holds exactly one personal-free flag:
handover:factory_pending. The first summon after speaks LINE_FACTORY
once, mint LOCAL, then never again; the drill markers died in the wipe,
so the reboot boots silent-clean. Enrollment owns the new commander.
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from tars.core import canon
from tars.core.voiceid import hash_passphrase

STAGE_KEY = "handover:stage"          # pass | confirm | keys | countdown
DEADLINE_KEY = "handover:deadline"    # epoch float — set only while stage == countdown
KEEP_KEYS_KEY = "handover:keep_keys"  # "yes"/"no" — Cooper's choice, recorded at the gate
FACTORY_KEY = "handover:factory_pending"  # "yes" post-wipe: the one greeting owed
COUNTDOWN_S = 10

# §30 wipe order — transactional per store, declared once (the battery pins the boundary laws)
WIPE_ORDER = ("vault", "profiles", "settings", "secrets", "brain", "logs")


class Handover:
    """The farewell engine: gate flow + countdown + ordered wipe. All local, zero ring."""

    def __init__(self, vault, bus, store, settings, log_path, brain_root=None,
                 secrets=None, ring=None, time_fn=None):
        import time as _time
        self._vault = vault
        self._store = store
        self._settings = settings
        self._log_path = Path(log_path)
        self._brain_root = Path(brain_root) if brain_root is not None \
            else Path(vault.path).parent / "tars-brain"
        self._secrets = secrets  # caller-provided mapping (nt truth: the AiO erases .env itself)
        self._ring = ring
        self._time = time_fn or _time.time
        # crash law: a countdown found on a reopened vault is DEAD — never resumed, never fired
        if vault.kv_get(STAGE_KEY) == "countdown":
            vault.kv_set(STAGE_KEY, "")
        self._bus = bus
        bus.subscribe(self._on_close)

    # ---------- the flow ----------

    def active(self):
        """The live stage ("pass" | "confirm" | "keys" | "countdown") or None."""
        stage = self._vault.kv_get(STAGE_KEY)
        return stage if stage in ("pass", "confirm", "keys", "countdown") else None

    def open(self, machine) -> list:
        """Gate 1: a verified Cooper-tier seat alone opens the farewell."""
        if machine.audience != "cooper":
            return [(canon.LINE_HANDOVER_VOICE_ONLY, "local", None)]
        self._vault.kv_set(STAGE_KEY, "pass")
        return [(canon.LINE_HANDOVER_PASS, "local", None)]

    def handle(self, t: str) -> list:
        """Consume the gated utterance (normalized text, per execute law). At the pass /
        confirm / keys stages an utterance that isn't the answer CANCELS honestly;
        during the countdown only the abort words are consumed — the rest is conversation."""
        stage = self.active()
        if stage == "pass":
            self._store.refresh()  # enrollment may have landed since this instance loaded
            credentials = self._store.pass_credentials()
            if credentials and hash_passphrase(t, credentials[0]) == credentials[1]:
                self._vault.kv_set(STAGE_KEY, "confirm")
                return [(canon.LINE_HANDOVER_CONFIRM, "local", None)]
            return self._abort()
        if stage == "confirm":
            if t == "confirm":
                self._vault.kv_set(STAGE_KEY, "keys")
                return [(canon.handover_keys_line(), "local", None)]
            return self._abort()
        if stage == "keys":
            if t in ("yes", "no"):
                self._vault.kv_set(KEEP_KEYS_KEY, "yes" if t == "yes" else "no")
                self._vault.kv_set(STAGE_KEY, "countdown")
                self._vault.kv_set(DEADLINE_KEY, str(self._time() + COUNTDOWN_S))
                return [(canon.handover_countdown_line(COUNTDOWN_S), "local", None)]
            return self._abort()
        if stage == "countdown" and t in ("abort handover", "cancel"):
            return self._abort()
        return []  # not ours to consume

    def _abort(self) -> list:
        self._vault.kv_set(STAGE_KEY, "")
        self._vault.kv_set(DEADLINE_KEY, "")
        return [(canon.LINE_HANDOVER_ABORTED, "local", None)]

    def _on_close(self, kind: str, detail) -> None:
        """Law 5 + sleep law: ANY close kills a live flow instantly — nothing is wiped."""
        if kind == "close" and self.active() is not None:
            self._vault.kv_set(STAGE_KEY, "")
            self._vault.kv_set(DEADLINE_KEY, "")

    def tick(self) -> bool:
        """The standing heartbeat seam: a crossed deadline fires the wipe. Truthful answer."""
        if self.active() != "countdown":
            return False
        if self._time() < float(self._vault.kv_get(DEADLINE_KEY) or 0):
            return False
        keep_keys = self._vault.kv_get(KEEP_KEYS_KEY) == "yes"
        self._wipe(keep_keys)  # the stage flags die inside the vault wipe — the goodbye is complete
        return True

    # ---------- the wipe (§30 ledger order; per-store transactional) ----------

    def _wipe(self, keep_keys: bool) -> None:
        steps = {"vault": self._wipe_vault, "profiles": self._wipe_profiles,
                 "settings": self._wipe_settings, "secrets": lambda: self._wipe_secrets(keep_keys),
                 "brain": self._wipe_brain, "logs": self._wipe_logs}
        for name in WIPE_ORDER:
            steps[name]()
        self._vault.kv_set(FACTORY_KEY, "yes")  # the one flag owed to the next commander

    def _wipe_vault(self) -> None:
        self._vault.wipe()  # one transaction inside vault.py — the store's own atomicity

    def _wipe_profiles(self) -> None:
        self._store.wipe()  # the standing Member File seam — atomic, factory-empty

    def _wipe_settings(self) -> None:
        self._settings.reset_factory()  # honesty 90 stands; dials return to birth

    def _wipe_secrets(self, keep_keys: bool) -> None:
        if keep_keys:
            return  # YES at the gate: the keys stand, byte for byte
        if self._secrets is not None:
            self._secrets.clear()  # disowned: the ring re-loads empty and refuses honestly
        if self._ring is not None:
            self._ring.disown()  # the live ring lets the keys go with them (keys.py seam)

    def _wipe_brain(self) -> None:
        if self._brain_root.is_dir():
            shutil.rmtree(self._brain_root)  # line 230: the mind goes with its commander

    def _wipe_logs(self) -> None:
        """personal entries purged; EXACTLY ONE line survives: Handover executed <date>."""
        day = datetime.now().date().isoformat()
        record = {"ts": datetime.now().isoformat(timespec="milliseconds"), "kind": "handover",
                  "note": f"Handover executed {day}"}  # raw line carries the phrase + the iso date
        payload = json.dumps(record, ensure_ascii=False) + "\n"
        tmp = self._log_path.with_name(self._log_path.name + ".tmp")
        with open(tmp, "wb") as fh:  # wb: fsync needs a WRITE descriptor on nt (msvcrt _commit); an rb fd passes Linux, dies on Windows
            fh.write(payload.encode("utf-8"))
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, self._log_path)  # atomic: a reader sees old bytes or the survivor, never half
