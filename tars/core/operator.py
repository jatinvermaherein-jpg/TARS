"""The hands: execution intents + adapters for operator rows.

Executor protocol (declared): one method per GREEN/RED intent, returning True
on performed. NtExecutor carries the REAL codepaths — every verb sits behind an
os.name == "nt" guard with a canon comment; in this Linux sandbox each one
answers False and nothing ever spawns (the battery asserts exactly that).
FixtureExecutor records every intent, in order — the ONLY executor tests drive.

The app alias map is a CLOSED, declared list (command-grammar §5 + declared
sane system verbs). Unknown tokens earn a clarifying question, never a launch.
"""
import os

# Declared, closed (grammar §5 + declared sane system verbs): alias token -> (display, launch id)
APP_ALIASES = {
    "chrome": ("Chrome", "chrome.exe"),
    "google chrome": ("Chrome", "chrome.exe"),
    "word": ("Word", "WINWORD.EXE"),
    "microsoft word": ("Word", "WINWORD.EXE"),
    "excel": ("Excel", "EXCEL.EXE"),
    "powerpoint": ("PowerPoint", "POWERPNT.EXE"),
    "settings": ("Settings", "ms-settings:"),
    "whatsapp": ("WhatsApp", "whatsapp:"),
    "telegram": ("Telegram", "telegram:"),
    "spotify": ("Spotify", "spotify:"),
    "calculator": ("Calculator", "calc.exe"),
    "notepad": ("Notepad", "notepad.exe"),
    "explorer": ("Explorer", "explorer.exe"),
    "file explorer": ("Explorer", "explorer.exe"),
}


class NtExecutor:
    """Real Windows execution — reviewable shapes, zero spawns off-nt."""

    def open_app(self, launch_id: str) -> bool:
        if os.name != "nt":
            return False  # canon: launches happen on the AiO — the sandbox only records intents
        os.startfile(launch_id)  # shell association: exe/scheme both resolve
        return True

    def close_app(self, display: str) -> bool:
        if os.name != "nt":
            return False  # canon: window control is an AiO verb
        import ctypes

        closed = {"hit": False}

        @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        def _each(hwnd, _lparam):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length:
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                if display.lower() in buf.value.lower():
                    ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE, politely
                    closed["hit"] = True
            return True

        ctypes.windll.user32.EnumWindows(_each, 0)
        return closed["hit"]

    def volume_up(self) -> bool:
        return self._volume_key(0xAF)  # VK_VOLUME_UP

    def volume_down(self) -> bool:
        return self._volume_key(0xAE)  # VK_VOLUME_DOWN

    def volume_mute(self) -> bool:
        return self._volume_key(0xAD)  # VK_VOLUME_MUTE

    def volume_set(self, level: int) -> bool:
        if os.name != "nt":
            return False  # canon: mixer control is an AiO verb
        # declared shape: zero the counter, then step up in declared 2-point presses
        for _n in range(50):
            self._volume_key(0xAE)
        for _n in range(max(0, min(100, level)) // 2):
            self._volume_key(0xAF)
        return True

    def _volume_key(self, vk: int) -> bool:
        if os.name != "nt":
            return False  # canon: media keys are AiO hardware intents
        import ctypes
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
        return True

    def brightness_up(self) -> bool:
        return self._brightness_step(10)

    def brightness_down(self) -> bool:
        return self._brightness_step(-10)

    def brightness_set(self, level: int) -> bool:
        if os.name != "nt":
            return False  # canon: panel control is an AiO verb
        import subprocess
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        f"(Get-WmiObject -ns root/wmi -class WmiMonitorBrightnessMethods)"
                        f".WmiSetBrightness(1,{max(0, min(100, level))})"], timeout=15)
        return True

    def _brightness_step(self, delta: int) -> bool:
        if os.name != "nt":
            return False  # canon: panel control is an AiO verb
        import subprocess
        script = ("$c=(Get-WmiObject -ns root/wmi -class WmiMonitorBrightness).CurrentBrightness;"
                  "$n=[math]::Max(0,[math]::Min(100,$c+(%d)));"
                  "(Get-WmiObject -ns root/wmi -class WmiMonitorBrightnessMethods).WmiSetBrightness(1,$n)" % delta)
        subprocess.run(["powershell", "-NoProfile", "-Command", script], timeout=15)
        return True

    def snap_left(self) -> bool:
        return self._snap_key(0x25)  # VK_LEFT

    def snap_right(self) -> bool:
        return self._snap_key(0x27)  # VK_RIGHT

    def snap_maximize(self) -> bool:
        return self._snap_key(0x26)  # VK_UP

    def _snap_key(self, vk: int) -> bool:
        if os.name != "nt":
            return False  # canon: window snap chords are AiO verbs
        import ctypes
        win = 0x5B  # VK_LWIN
        ctypes.windll.user32.keybd_event(win, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
        ctypes.windll.user32.keybd_event(win, 0, 2, 0)
        return True

    def open_url(self, url: str) -> bool:
        if os.name != "nt":
            return False  # canon: the OS browser hand-off happens on the AiO
        os.startfile(url)
        return True

    def delete_path(self, target: str) -> bool:
        if os.name != "nt":
            return False  # canon: filesystem writes happen on the AiO, behind the typed-YES gate
        os.remove(target)
        return True

    def move_path(self, source: str, dest: str) -> bool:
        if os.name != "nt":
            return False  # canon: filesystem writes happen on the AiO, behind the typed-YES gate
        import shutil
        shutil.move(source, dest)
        return True

    def power(self, verb: str, countdown_s: int) -> bool:
        if os.name != "nt":
            return False  # canon: power verbs touch the family machine only after typed YES, on the AiO
        import subprocess
        flag = {"shutdown": "/s", "restart": "/r", "sleep": "/h"}[verb]
        try:
            result = subprocess.run(["shutdown", flag, "/t", str(countdown_s)],
                                    timeout=10, capture_output=True)
        except (OSError, subprocess.SubprocessError):
            return False  # spawn refused — the ack must report the refusal, not hope
        return result.returncode == 0  # merge-day field law: a non-zero exit is NOT a performed verb


class FixtureExecutor:
    """The sandbox's hands: records every intent in order, performs nothing."""

    def __init__(self):
        self.calls = []

    def open_app(self, launch_id: str) -> bool:
        self.calls.append(("open_app", launch_id))
        return True

    def close_app(self, display: str) -> bool:
        self.calls.append(("close_app", display))
        return True

    def volume_up(self) -> bool:
        self.calls.append(("volume_up",))
        return True

    def volume_down(self) -> bool:
        self.calls.append(("volume_down",))
        return True

    def volume_mute(self) -> bool:
        self.calls.append(("volume_mute",))
        return True

    def volume_set(self, level: int) -> bool:
        self.calls.append(("volume_set", level))
        return True

    def brightness_up(self) -> bool:
        self.calls.append(("brightness_up",))
        return True

    def brightness_down(self) -> bool:
        self.calls.append(("brightness_down",))
        return True

    def brightness_set(self, level: int) -> bool:
        self.calls.append(("brightness_set", level))
        return True

    def snap_left(self) -> bool:
        self.calls.append(("snap_left",))
        return True

    def snap_right(self) -> bool:
        self.calls.append(("snap_right",))
        return True

    def snap_maximize(self) -> bool:
        self.calls.append(("snap_maximize",))
        return True

    def open_url(self, url: str) -> bool:
        self.calls.append(("open_url", url))
        return True

    def delete_path(self, target: str) -> bool:
        self.calls.append(("delete_path", target))
        return True

    def move_path(self, source: str, dest: str) -> bool:
        self.calls.append(("move_path", source, dest))
        return True

    def power(self, verb: str, countdown_s: int) -> bool:
        self.calls.append(("power", verb, countdown_s))
        return True
