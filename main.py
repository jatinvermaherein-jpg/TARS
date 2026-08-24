"""TARS bridge host — P3 Merge Day. Architect mint (canon root: the M-plan P3.1 row
decreed `python main.py`; the two lanes never wrote here, so the joint is minted
against their frozen contract shapes, not by crossing either lane).

One file, three promises (bridge-contract §3/§6):
  1. `window.tarsBridge` = the real runtime — Dialog/Router/Machine/Vault, exactly
     the objects the 708-check ceremony proved. No shadow code-paths.
  2. Every bus event is pumped to `window.__tarsEvent({type, ...detail})` —
     APP-registered, core-defensive: a missing handler must never crash the core.
  3. The network stays cold until a real message is sent; keys load only from
     C:\\TARS\\secrets.env (never committed, never printed).

Tonight's honest absences (declared, never faked): the ears stack stages at M-2,
so push-to-talk rides the real turn seam and answers the byte-exact §22 no-mic
row; whisper/piper model files land with the M-2 ritual and report honestly
absent until then.
"""
import json
import os
import shutil
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from tars.core import canon
from tars.core.adapters import GroqAdapter, OpenRouterAdapter
from tars.core.bus import Bus
from tars.core.capture import SoundDeviceCapture
from tars.core.dialog import Dialog
from tars.core.ears import EarLadder, GroqEarsAdapter, WhisperSmallLocal, run_voice_turn
from tars.core.enroll import list_members as enroll_list_members
from tars.core.gauge import gauge_rows
from tars.core.keys import load_ring, parse_env_file
from tars.core.logx import LogX
from tars.core.mouth import EdgeTier, Mouth, PiperTier, SapiTier
from tars.core.router import Router
from tars.core.settings import Settings
from tars.core.state import Machine
from tars.core.vault import Vault
from tars.core.voiceid import ProfileStore

try:
    import webview  # pywebview: the shell host. Staged in the AiO venv (M-1.5).
except ImportError:  # headless sandbox: the Bridge object still assembles + answers
    webview = None

REPO_ROOT = Path(__file__).resolve().parent
APP_DIR = REPO_ROOT / "tars" / "app"
APP_INDEX = APP_DIR / "index.html"
DEFAULT_DATA = Path(r"C:\TARS\data") if os.name == "nt" else Path.home() / ".tars"
TICK_S = 1.0  # the heartbeat: clock dues, speak-queue drain, idle law

# The one parse-time element of merge glue (P3 first-run finds, round two). Docs:
# window.pywebview.api is only GUARANTEED at pywebviewready — never at parse. A bare
# alias therefore races the mock (parse-order: alias script -> mock.js). So the host
# serves a DEFERRED PROXY that owns window.tarsBridge from parse onward: any JS call
# made before the bridge is ready is queued and replayed onto the real api the
# instant pywebviewready fires; the mock sees the name taken and never installs.
# In a plain browser the file bundle is untouched — contract §6's mock law stands.
_ALIAS = (b"<script>(function(){var pending=[],real=null;"
          b"window.tarsBridge=new Proxy({}, {get:function(t,name){"
          b"if(name===\"then\"){return undefined;}"
          b"return function(){var a=Array.prototype.slice.call(arguments);"
          b"if(real){return real[name].apply(real,a);}"
          b"return new Promise(function(res,rej){pending.push({n:name,a:a,res:res,rej:rej});});};}});"
          b"window.addEventListener(\"pywebviewready\",function(){"
          b"real=window.pywebview.api;window.tarsBridge=real;"
          b"pending.forEach(function(c){real[c.n].apply(real,c.a).then(c.res,c.rej);});pending=[];});"
          b"})();</script>")


def patched_index(raw: bytes) -> bytes:
    """index.html bytes + the alias, injected right after <head>; if the marker ever
    moves, serve the file untouched and log nothing here — the mock law stays safe."""
    return raw.replace(b"<head>", b"<head>\n" + _ALIAS, 1)


class _AppHandler(SimpleHTTPRequestHandler):
    """Loopback static host for tars/app/*; quiet, byte-true, and only index.html patched."""

    def log_message(self, *args) -> None:  # the app never chatters to the terminal
        pass

    def do_GET(self) -> None:
        if self.path.split("?", 1)[0] in ("/", "/index.html"):
            try:
                body = patched_index(APP_INDEX.read_bytes())
            except OSError:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


def serve_app() -> tuple:
    """Start the loopback host on an ephemeral port. Thread is a daemon: it dies
    with the window. Bound to 127.0.0.1 only — the bridge is a private place."""
    import functools
    handler = functools.partial(_AppHandler, directory=str(APP_DIR))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.2},
                              daemon=True, name="tars-appserver")
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/index.html"


def _data_dir() -> Path:
    return Path(os.environ.get("TARS_DATA", str(DEFAULT_DATA)))


def build_runtime(data_dir: Path) -> dict:
    """Assemble the production runtime cold-off (Law 3). Wire-cold: adapters hold
    no sockets; keys arrive only from secrets.env when Cooper places it."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    log = LogX(data_dir / "logs.jsonl")
    settings = Settings.load(data_dir / "settings.json", log)
    vault = Vault(data_dir / "vault.db")
    bus = Bus()
    machine = Machine(settings, log, bus)
    secrets = data_dir.parent / "secrets.env"
    source = parse_env_file(secrets) if secrets.is_file() else {}  # absent file == empty ring, honest lines
    ring = load_ring(source)
    router = Router(ring, {"groq": GroqAdapter(), "openrouter": OpenRouterAdapter()}, vault, bus)
    dialog = Dialog(settings, vault, router, machine, bus)  # ctor builds the full command layer
    voice_dir = data_dir / "voice"  # M-2 stages tars-piper.onnx / whisper-small.bin here
    mouth = Mouth([PiperTier(voice_dir), SapiTier(), EdgeTier()], log)  # M-2.1: anointed voice speaks first
    ladder = EarLadder([WhisperSmallLocal(voice_dir), GroqEarsAdapter(ring)], log)
    store = ProfileStore(data_dir / "profiles.json", log)
    return {"log": log, "settings": settings, "vault": vault, "bus": bus, "machine": machine,
            "ring": ring, "router": router, "dialog": dialog, "mouth": mouth,
            "ladder": ladder, "store": store, "started": time.monotonic()}


class Bridge:
    """The js_api surface, method-for-method per contract §3. Thin glue only:
    every answer is minted by the ceremony-proven core objects, never here."""

    def __init__(self, rt: dict):
        self._rt = rt

    # --- conversation surface -------------------------------------------------
    def send(self, text) -> dict:
        return self._rt["dialog"].send(text)

    def list_chats(self) -> list:
        return self._rt["dialog"].list_chats()

    def open_chat(self, id) -> list:  # noqa: A002 - the contract names it id
        return self._rt["dialog"].open_chat(id)

    def new_chat(self) -> dict:
        return self._rt["dialog"].new_chat()

    def confirm(self, actionId, yes=False) -> dict:  # noqa: N803 - contract §3 name
        return self._rt["dialog"].confirm(actionId, bool(yes))

    def quick_action(self, name, payload=None) -> dict:
        return self._rt["dialog"].quick_action(name, payload if isinstance(payload, dict) else {})

    # --- dials + state --------------------------------------------------------
    def get_state(self) -> dict:
        return self._rt["machine"].notice()

    def summon(self) -> dict:
        """[A5] The OFF cover's door. The lawful summon with zero message and zero
        ring spend — the exact transition send() performs on a first text. _go
        already emits the state event; the cover lifts on that envelope."""
        machine = self._rt["machine"]
        machine.summon()  # OFF -> ARMED; an honest no-op when already awake
        return machine.notice()

    def set_dial(self, name, value) -> dict:
        if isinstance(value, float) and value.is_integer():
            value = int(value)  # browser numbers arrive double; the dial law rules ints
        result = self._rt["settings"].set_dial(name, value)
        if result.get("ok"):
            self._rt["machine"].emit_notice()  # dials move live (demochat scene 4 law)
        return result

    # --- voice door (ears stack stages at M-2; tonight the seam answers §22) ---
    def voice_ptt(self, phase) -> None:
        if phase != "start":
            return  # the one-shot turn is tonight's whole press; continuous PTT ships with M-2
        machine = self._rt["machine"]
        if machine.state == "off":
            machine.summon()  # a mic press implies a summoned app, same law as send()
        run_voice_turn(SoundDeviceCapture(machine), self._rt["ladder"], machine,
                       self._rt["bus"], self._rt["dialog"], mouth=self._rt["mouth"])

    # --- reports + explorers ---------------------------------------------------
    def get_status(self) -> dict:
        rt = self._rt
        try:
            import psutil  # staged at M-1.5; absent == an honestly zeroed meter
            ram_mb = int(psutil.Process(os.getpid()).memory_info().rss // (1024 ** 2))
        except ImportError:
            ram_mb = 0
        try:
            free_gb = int(shutil.disk_usage(str(rt["vault"].path.parent)).free //(1024 ** 3))
        except OSError:
            free_gb = 0
        return {
            "keys": gauge_rows(rt["ring"]),
            "ram": {"mb": ram_mb, "ceiling": 2000},
            "storage": {"vaultMb": _size_mb(rt["vault"].path),
                        "brainMb": _size_mb(rt["vault"].path.parent / "tars-brain"),
                        "diskFreeGb": free_gb},
            "uptimeS": int(time.monotonic() - rt["started"]),
            "powerNote": None,  # the power meter lands with M-3's UPS; null is the honest answer
            "windowsUpdate": "",  # A3 slot: a Windows-update watch text is not built — empty is honest (APP may hide)
        }

    def list_members(self) -> list:
        return enroll_list_members(self._rt["store"])

    def list_brain(self, path="") -> list:
        return self._rt["dialog"].list_brain(path)

    def brain_text(self, path):
        return self._rt["dialog"].brain_text(path)


def _size_mb(root) -> int:
    """Watcher's honest sizing law mirrored in glue (visibility §29, never a gate)."""
    root = Path(root)
    if root.is_file():
        return int(root.stat().st_size // (1024 ** 2))
    if not root.is_dir():
        return 0
    total = 0
    for dirpath, _dirs, files in os.walk(str(root)):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(dirpath, name))
            except OSError:
                continue
    return int(total // (1024 ** 2))


def make_pump(rt: dict) -> None:
    """Bus -> window.__tarsEvent. The try/except is contract law: a missing JS
    handler never crashes the core. Pre-load events drop silently (APP boots cold)."""
    def handler(kind: str, detail) -> None:
        window = rt.get("window")
        if window is None:
            return
        try:
            window.evaluate_js("window.__tarsEvent(%s)" % json.dumps({"type": kind, **(detail or {})}))
        except Exception:  # noqa: BLE001 - the contract's defensive-wrap clause, verbatim
            pass
    rt["bus"].subscribe(handler)


def boot(rt: dict) -> None:
    """Cold-open ritual (§7.1): a fresh chat id + the canon boot line. The machine
    stays OFF — the first real send performs the lawful summon (survival/factory
    confessions ride the send path, spoken exactly once, per the drill laws)."""
    chat_id = rt["dialog"].new_chat()["id"]
    rt["machine"].set_context(None, "local")
    rt["bus"].emit("chunk", {"chatId": chat_id, "seq": 0, "text": canon.LINE_BOOT})
    rt["bus"].emit("done", {"chatId": chat_id, "hue": "local", "lane": None})


def close_ritual(rt: dict) -> None:
    """Window died: the standing close seam does the work (drill clean-mark, brain
    fold via the bus — fold is byte-idempotent, a double close is safe), then the
    stores settle. Never throw on the way out."""
    try:
        rt["bus"].emit("close", {"reason": "stand down"})
    finally:
        rt["vault"].close()
        rt["log"].close()


def heartbeat(rt: dict, stop: threading.Event) -> None:
    """1s pump: clock dues fire, the speak queue drains, the idle law stands TARS
    down and the window follows (§7.10). A beat may fail; the loop may not die."""
    while not stop.wait(TICK_S):
        try:
            rt["dialog"].tick_clock()
            rt["mouth"].drain_speak_queue(rt["vault"], rt["machine"])
            if rt["machine"].check_idle():
                rt["machine"].stand_down("idle")
                rt["mouth"].drain_speak_queue(rt["vault"], rt["machine"])  # the idle-off line still speaks
                rt["bus"].emit("close", {"reason": "idle stand-down"})
                window = rt.get("window")
                if window is not None:
                    try:
                        window.destroy()
                    except Exception:  # noqa: BLE001 - close ritual covers any destroy-time race
                        pass
                return
        except Exception as exc:  # noqa: BLE001 - the pump reports and lives
            rt["log"].entry("host", note=f"heartbeat beat failed: {exc}")


def _start_hotkeys(rt) -> None:
    """P3.5 — the global summon chord (Ctrl+Alt+T) and kill chord (Ctrl+Alt+Esc),
    heard anywhere in Windows. PowerToys remaps the physical Copilot key onto
    Ctrl+Alt+T (bench manual); this hook is the ear that obeys it. Root-glue law:
    honest absence off-nt; a colliding registration means the chord stands down
    with a log line, never a fight."""
    if os.name != "nt":
        return
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    mods = 0x0002 | 0x0001 | 0x4000  # MOD_CONTROL | MOD_ALT | MOD_NOREPEAT — the About-panel chords
    wm_hotkey = 0x0312
    ready = threading.Event()
    holder = {"tid": None, "armed": False}

    def _summon():
        machine = rt["machine"]
        machine.summon()  # the lawful wake; an honest no-op when already awake (A5's own law)
        window = rt.get("window")
        if window is None:
            return
        try:
            window.restore()  # un-minimize; a courtesy on backends that know it
        except Exception:  # noqa: BLE001 — never crash the chord
            pass
        hwnd = getattr(window, "hwnd", None)
        if hwnd:
            try:
                user32.SetForegroundWindow(hwnd)
            except Exception:  # noqa: BLE001 — focus is a courtesy, never a crash
                pass

    def _kill():
        window = rt.get("window")
        if window is None:
            return
        try:
            window.destroy()  # main's finally-block close ritual does the honest rest
        except Exception:  # noqa: BLE001
            pass

    def _loop():
        holder["tid"] = kernel32.GetCurrentThreadId()
        holder["armed"] = bool(user32.RegisterHotKey(None, 1, mods, 0x54)          # Ctrl+Alt+T
                               and user32.RegisterHotKey(None, 2, mods, 0x1B))      # Ctrl+Alt+Esc
        ready.set()
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message != wm_hotkey:
                continue
            (_summon if msg.wParam == 1 else _kill)()

    threading.Thread(target=_loop, name="tars-hotkeys", daemon=True).start()
    if ready.wait(5) and holder["armed"]:
        rt["log"].entry("host", note="global chords armed: Ctrl+Alt+T summon, Ctrl+Alt+Esc kill")
    else:
        rt["log"].entry("host", note="global chords refused (a prior claim holds them) — keyboard quiet tonight")


def main() -> int:
    if webview is None:
        print("pywebview is not staged here — on the AiO, wake the venv first: "
              r"C:\TARS\.venv\Scripts\Activate.ps1 (M-1.5 stages pywebview inside it).", file=sys.stderr)
        return 2
    rt = build_runtime(_data_dir())
    make_pump(rt)
    stop = threading.Event()
    server, url = serve_app()
    window = webview.create_window("TARS", url, js_api=Bridge(rt),
                                   width=1240, height=780, min_size=(960, 620))
    rt["window"] = window
    _start_hotkeys(rt)  # P3.5: the summon/kill chords — daemon thread, honest no-op off-nt
    try:
        window.events.loaded += lambda: boot(rt)  # empty state + canon boot line (§7.1)
    except AttributeError:
        pass  # older pywebview: boot lands cosmetically late — the APP keeps its empty state
    pump = threading.Thread(target=heartbeat, args=(rt, stop), daemon=True, name="tars-heartbeat")
    pump.start()
    try:
        webview.start()  # blocks until the window closes (no debug server, no menu)
    finally:
        stop.set()
        server.shutdown()
        pump.join(timeout=2)
        close_ritual(rt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
