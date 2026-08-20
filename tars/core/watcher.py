"""The Watcher (bible §21 Tier-3 — the desk reads its own pulse).

Four doctrines rule this file, all battery-pinned:

§29 — METER = VISIBILITY, NOT ENFORCEMENT (canon comment law): storage_report
shows sizes and free space; NOTHING in this module refuses, blocks, throttles,
or deletes on size — a gentle advisory past a declared soft-mark is
visibility, never a cage. There is deliberately no enforcement branch here
(the battery greps for one and must find none).

§16 — reading-or-honest-line: every meter answers a LIVE reading through the
ONE ops seam, or the canon unavailable line. Never an invented digit.

Law 3 — TARS never auto-starts, and the watcher POLICES ITSELF: any
"tars"-named entry in a startup set is reported as a first-class violation,
ahead of the ordinary creep list.

The power-cut drill (§32 + the line-62 flavor): every run marks itself dirty
at boot and clean at stand-down/kill (the standing close event flips it). A
dirty prior run = a power event; the FIRST summon after speaks the survival
report ONCE, before anything else is answered; a boot after an outage is
OFF, always — nothing summons itself.

Ring math rides gauge.py/keys.py exactly as they stand — zero duplicated
counter logic in this file.
"""
from datetime import datetime

from tars.core import canon, gauge

# --- power-cut drill kv schema (vault law: kv holds point-in-time state, WAL+FULL durable)
DRILL_LAST_BOOT = "drill:last_boot"     # iso stamp of the CURRENT run's boot
DRILL_CLEAN = "drill:clean_exit"        # "yes" after stand-down/kill; a crash leaves it "no"


def drill_boot(vault, now=None) -> dict:
    """Run-start marker, Law 3 shaped: the previous run dirty => a power event to confess.
    Returns {"when": <iso>} to speak on the first summon, else None. Either way the
    CURRENT run boots marked dirty — innocent only after a clean exit proves it."""
    moment = (now or datetime.now()).isoformat(timespec="seconds")
    survival = None
    if vault.kv_get(DRILL_CLEAN) == "no" and vault.kv_get(DRILL_LAST_BOOT):
        survival = {"when": vault.kv_get(DRILL_LAST_BOOT)}
    vault.kv_set(DRILL_LAST_BOOT, moment)
    vault.kv_set(DRILL_CLEAN, "no")
    return survival


def drill_mark_clean(vault) -> None:
    """Any clean end (stand-down or the kill-switch — both ride the standing close event)."""
    vault.kv_set(DRILL_CLEAN, "yes")


def survival_probe(vault) -> list:
    """What the outage cost: an honest list of lost stores ([] = intact). Append-only laws
    make damage rare — the probe names exactly what it can verify, no sadder, no happier."""
    losses = []
    try:
        if vault.integrity() != "ok":
            losses.append("the vault's newest rows")
    except Exception:
        losses.append("the vault's newest rows")
    return losses


def survival_line(vault, when_iso: str) -> str:
    """The drill's voice: intact case is the line-62 flavor verbatim; damage names its losses.
    The clock-face is the honest 12-hour read of the last heartbeat stamp."""
    stamp = datetime.fromisoformat(str(when_iso))
    hour = stamp.hour % 12 or 12
    when = f"{hour}:{stamp.minute:02d} {'AM' if stamp.hour < 12 else 'PM'}"
    losses = survival_probe(vault)
    if losses:
        return canon.power_event_damage_line(when, losses)
    return canon.power_event_line(when)


class NtCreepSource:
    """READ-ONLY startup enumeration — real on the AiO, honestly absent anywhere else."""

    _RUN_KEYS = (("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Run"),
                 ("HKLM", r"Software\Microsoft\Windows\CurrentVersion\Run"))

    def snapshot(self):
        """-> sorted [entry names] on nt; False off-nt (the unavailable law, never a guess)."""
        import os
        if os.name != "nt":
            return False  # canon: the registry belongs to the AiO; the sandbox declines to invent it
        import winreg  # canon: nt-only seam, read-only
        names = []
        for hive_name, path in self._RUN_KEYS:
            hive = winreg.HKEY_CURRENT_USER if hive_name == "HKCU" else winreg.HKEY_LOCAL_MACHINE
            try:
                with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
                    idx = 0
                    while True:
                        try:
                            names.append(winreg.EnumValue(key, idx)[0])
                            idx += 1
                        except OSError:
                            break
            except OSError:
                continue  # a hive that won't open narrows the view honestly, never crashes the meter
        return sorted(names)


class FixtureCreepSource:
    """The suite's startup set: baseline + current both scripted; change events replayable."""

    def __init__(self, entries=()):
        self._entries = list(entries)
        self.calls = 0

    def snapshot(self):
        self.calls += 1
        return sorted(self._entries)

    def add(self, name: str) -> None:
        self._entries.append(name)


class Watcher:
    """One reader for the desk's pulse: gauge, storage, RAM, uptime, creep, the digest."""

    CREEP_BASELINE_KV = "creep:baseline"  # first snapshot is the honest baseline — declared
    SOFT_FREE_GB = 2                      # §29 advisory mark: visibility, never a block

    def __init__(self, ring, ops, vault, creep=None, time_fn=None):
        import time as _time
        self._ring = ring
        self._ops = ops
        self._vault = vault
        self._creep = creep if creep is not None else NtCreepSource()
        self._time = time_fn or _time.time

    # --- the gauge (keys.py/gauge.py math, as they stand) ---

    def gauge_report(self) -> str:
        rows = gauge.gauge_rows(self._ring)
        names = self._ring_names()
        lines = [f"{i + 1}. {names[i]} {row['lane']}: {row['remainingPct']}% left, {row['state']}."
                 for i, row in enumerate(rows)]
        healthy = [r for r in rows if r["state"] == "ok"]
        warn = [r for r in rows if r["state"] == "warn"]
        spent = [r for r in rows if r["state"] == "spent"]
        return ("Key gauge:\n" + "\n".join(lines) + "\n"
                + canon.keys_summary_line(len(healthy), len(rows), len(warn), len(spent)))

    def _ring_names(self) -> list:
        return [key.visible_name for key in self._ring.keys()]

    # --- meters (§29 visibility-only; §16 honest lines) ---

    def storage_report(self, brain_dir=None, free_root="/") -> str:
        return self.storage_line(brain_dir, free_root)["line"]

    def storage_line(self, brain_dir=None, free_root="/") -> dict:
        """Meter-only render (§29): sizes + free space + the doctrine tail. NO branch here
        may refuse or block on size — the advisory is a sentence, never a gate."""
        vault_mb = self._dir_size_mb(self._vault.path)
        brain = brain_dir or str(self._vault.path.parent / "tars-brain")
        brain_mb = self._dir_size_mb(brain)
        try:
            free_gb = int(self._ops.storage_free_bytes(free_root) // (1024 ** 3))
            advisory = free_gb < self.SOFT_FREE_GB
        except (OSError, TypeError):
            return {"ok": False, "line": canon.meter_unavailable_line("The storage meter")}
        return {"ok": True, "advisory": advisory,
                "line": canon.storage_meter_line(vault_mb, brain_mb, free_gb, advisory)}

    def _dir_size_mb(self, root) -> int:
        import os
        if os.path.isfile(str(root)):
            return int(os.path.getsize(str(root)) // (1024 ** 2))
        total = 0
        if not os.path.isdir(str(root)):
            return 0  # a brain that was never grown honestly measures zero
        for dirpath, _dirs, files in os.walk(str(root)):
            for name in files:
                try:
                    total += os.path.getsize(os.path.join(dirpath, name))
                except OSError:
                    continue
        return int(total // (1024 ** 2))

    def ram_report(self) -> str:
        percent = self._ops.ram_percent()
        if percent is False:
            return canon.meter_unavailable_line("The RAM meter")
        return canon.ram_ack(percent)

    def uptime_report(self) -> str:
        seconds = self._ops.uptime_seconds()
        if seconds is False:
            return canon.meter_unavailable_line("The uptime meter")
        return canon.uptime_ack(int(seconds // 3600))

    # --- startup-creep watch (Law 3 self-policing FIRST) ---

    def creep_report(self) -> str:
        names = self._creep.snapshot()
        if names is False:
            return canon.meter_unavailable_line("The startup watch")
        violations = [n for n in names if "tars" in n.lower()]
        if violations:
            return "\n".join(canon.creep_violation_line(n) for n in violations)  # Law 3 flags first
        import json as _json
        raw = self._vault.kv_get(self.CREEP_BASELINE_KV)
        if raw is None:
            self._vault.kv_set(self.CREEP_BASELINE_KV, _json.dumps(names))
            return canon.LINE_STARTUP_CLEAN  # first honest snapshot becomes the baseline
        baseline = set(_json.loads(raw))
        additions = [n for n in names if n not in baseline]
        if not additions:
            return canon.LINE_STARTUP_CLEAN
        return ("Startup creep:\n" + "\n".join(
            f"{i + 1}. {canon.creep_line(n)}" for i, n in enumerate(additions)))

    # --- the one-shot digest (powers the `status` row AND the rostered chip) ---

    def status_report(self) -> str:
        rows = gauge.gauge_rows(self._ring)
        healthy = [r for r in rows if r["state"] == "ok"]
        warn = [r for r in rows if r["state"] == "warn"]
        spent = [r for r in rows if r["state"] == "spent"]
        return "\n".join([
            canon.keys_summary_line(len(healthy), len(rows), len(warn), len(spent)),
            self.storage_report(),
            self.ram_report(),
            self.creep_report(),
            self.uptime_report(),
        ])
