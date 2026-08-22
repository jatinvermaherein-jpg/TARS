"""Daily ops hands (P-CORE-6): screenshot, clipboard, uptime/RAM/storage/CPU-hog.

SystemOps protocol (declared): one method per meter/deed. NtOps carries the REAL
codepaths — every OS-specific verb sits behind os.name == "nt" with a canon
comment and answers False off-nt (the standing law); storage_free_bytes is the
honest exception: shutil.disk_usage is stdlib on every OS, so the reading is
REAL in the sandbox too. FixtureOps records every call and answers scripted
values (clipboard round-trips through its own store off-nt).

P-CORE-8: capture_frame() is LOOK's end of the ONE capture path (_grab) — the
same BitBlt deed, but the frame returns as RAM bytes (never a file, §19) while
screenshot() keeps writing the Desktop artifact (§18).

Zero-dep doctrine: the PNG writer is ~40 lines of zlib+struct — NO PIL ever.
psutil is OPTIONAL for the CPU-hog meter on nt; never required, never imported
off-nt (an unavailable meter answers the canon line, not a guess).
"""
import os
import shutil
import struct
import zlib


def png_bytes(width: int, height: int, rgb_rows: bytes) -> bytes:
    """Pure-stdlib PNG: signature + IHDR + IDAT (filter 0 rows) + IEND. rgb_rows is the
    raw pixel block, width*height*3 bytes, row-major. Deterministic by construction."""

    def _chunk(tag: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    if len(rgb_rows) != width * height * 3:
        raise ValueError("pixel block size mismatch")
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit truecolor RGB
    stride = width * 3
    raw = b"".join(b"\x00" + rgb_rows[row * stride:(row + 1) * stride] for row in range(height))
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header)
            + _chunk(b"IDAT", zlib.compress(raw, 6)) + _chunk(b"IEND", b""))


class NtOps:
    """Real Windows daily ops — reviewable shapes, refusal-False off-nt."""

    def uptime_seconds(self):
        if os.name != "nt":
            return False  # canon: uptime belongs to the family machine; the sandbox declines to invent it
        import ctypes
        return ctypes.windll.kernel32.GetTickCount64() / 1000.0  # ms since boot, no WMI round-trip

    def ram_percent(self):
        if os.name != "nt":
            return False  # canon: memory pressure is the AiO's business
        import ctypes

        class _MEMSTAT(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

        statex = _MEMSTAT()
        statex.dwLength = ctypes.sizeof(_MEMSTAT)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(statex))
        return int(statex.dwMemoryLoad)

    def storage_free_bytes(self, root: str) -> int:
        return shutil.disk_usage(root).free  # stdlib on every OS — the honest dual path (REAL here too)

    def cpu_hog(self):
        if os.name != "nt":
            return False  # canon: process tables are AiO-local; no invented numbers
        try:
            import psutil  # OPTIONAL on the AiO — the meter darkens honestly without it
        except ImportError:
            return False
        psutil.cpu_percent(interval=None)
        import time as _time
        _time.sleep(0.1)  # the sampler needs one breath between readings
        top = None
        for proc in psutil.process_iter(["name", "cpu_percent"]):
            try:
                info = proc.info
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            if info["cpu_percent"] and (top is None or info["cpu_percent"] > top[1]):
                top = (info["name"], int(round(info["cpu_percent"])))
        return top

    def clipboard_get(self):
        if os.name != "nt":
            return False  # canon: the clipboard belongs to the AiO's user, not the sandbox
        import ctypes
        user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
        if not user32.OpenClipboard(None):
            return ""
        try:
            handle = user32.GetClipboardData(13)  # CF_UNICODETEXT
            if not handle:
                return ""
            locked = kernel32.GlobalLock(handle)
            if not locked:
                return ""
            try:
                return ctypes.wstring_at(locked)
            finally:
                kernel32.GlobalUnlock(handle)
        finally:
            user32.CloseClipboard()

    def clipboard_set(self, text: str) -> bool:
        if os.name != "nt":
            return False  # canon: as above — the sandbox never wears Cooper's clipboard
        import ctypes
        user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
        data = str(text).encode("utf-16-le") + b"\x00\x00"
        handle = kernel32.GlobalAlloc(0x0042, len(data))  # GMEM_MOVEABLE | GMEM_ZEROINIT
        locked = kernel32.GlobalLock(handle)
        ctypes.memmove(locked, data, len(data))
        kernel32.GlobalUnlock(handle)
        if not user32.OpenClipboard(None):
            return False
        try:
            user32.EmptyClipboard()
            return bool(user32.SetClipboardData(13, handle))  # CF_UNICODETEXT
        finally:
            user32.CloseClipboard()

    def _grab(self):
        """The ONE capture path (canon): BitBlt the primary display -> top-down RGB rows.
        Off-nt answers False — AiO deed. Callers decide the destination: screenshot()
        writes the Desktop PNG (the §18 artifact); capture_frame() hands RAM bytes to
        LOOK (§19 — never a file)."""
        if os.name != "nt":
            return False  # canon: BitBlt is an AiO deed; off-nt the row answers, not pretends
        import ctypes
        user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
        width = user32.GetSystemMetrics(0)  # SM_CXSCREEN — full capture this era ("region" = P3's lasso)
        height = user32.GetSystemMetrics(1)
        src = user32.GetDC(0)
        mem = gdi32.CreateCompatibleDC(src)
        bitmap = gdi32.CreateCompatibleBitmap(src, width, height)
        gdi32.SelectObject(mem, bitmap)
        gdi32.BitBlt(mem, 0, 0, width, height, src, 0, 0, 0x00CC0020)  # SRCCOPY
        # BGRA pull bottom-up, flip to top-down RGB rows for the PNG writer
        buf = ctypes.create_string_buffer(width * height * 4)

        class _BMPINFO(ctypes.Structure):
            _fields_ = [("bmiHeader", ctypes.c_byte * 40), ("bmiColors", ctypes.c_byte * 16)]

        info = _BMPINFO()
        ctypes.memset(ctypes.byref(info), 0, ctypes.sizeof(info))  # byref: memset wants a POINTER, not the instance (AiO ceremony traceback)
        header = struct.pack("<IiiHHIIiiII", 40, width, -height, 1, 32, 0, 0, 0, 0, 0, 0)
        ctypes.memmove(info.bmiHeader, header, 40)
        gdi32.GetDIBits(mem, bitmap, 0, height, buf, ctypes.byref(info), 0)  # byref: out-structs always ride pointers
        rows = bytearray(width * height * 3)
        for row in range(height):
            for col in range(width):
                base = (row * width + col) * 4
                rows[(row * width + col) * 3:(row * width + col) * 3 + 3] = \
                    bytes((buf[base + 2], buf[base + 1], buf[base]))
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(mem)
        user32.ReleaseDC(0, src)
        return width, height, bytes(rows)

    def screenshot(self, kind: str, dest_dir: str):
        grabbed = self._grab()
        if grabbed is False:
            return False
        width, height, rows = grabbed
        os.makedirs(dest_dir, exist_ok=True)
        name = os.path.join(dest_dir, "screenshot.png")
        with open(name, "wb") as fh:
            fh.write(png_bytes(width, height, rows))
        return name

    def capture_frame(self):
        """LOOK's raw material: (png_bytes, window_title, visible_text) in RAM — NEVER a file.
        Visible text needs OCR (M-era); the title rides with the frame for the classifier."""
        grabbed = self._grab()
        if grabbed is False:
            return False
        width, height, rows = grabbed
        import ctypes
        user32 = ctypes.windll.user32  # canon: foreground-title read is an nt-only seam
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        title_buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, title_buf, length + 1)
        return png_bytes(width, height, rows), title_buf.value, ""


class FixtureOps:
    """The sandbox's daily-ops twin: records calls, answers scripted values, round-trips the clip."""

    def __init__(self, scripted=None):
        self.calls = []
        self._scripted = dict(scripted or {})
        self._clip = ""

    def uptime_seconds(self):
        self.calls.append(("uptime_seconds",))
        return self._scripted.get("uptime_seconds", False)

    def ram_percent(self):
        self.calls.append(("ram_percent",))
        return self._scripted.get("ram_percent", False)

    def storage_free_bytes(self, root: str) -> int:
        self.calls.append(("storage_free_bytes", root))
        return self._scripted.get("storage_free_bytes", 0)

    def cpu_hog(self):
        self.calls.append(("cpu_hog",))
        return self._scripted.get("cpu_hog", False)

    def clipboard_get(self):
        self.calls.append(("clipboard_get",))
        return self._clip

    def clipboard_set(self, text: str) -> bool:
        self.calls.append(("clipboard_set", str(text)))
        self._clip = str(text)
        return True

    def screenshot(self, kind: str, dest_dir: str):
        self.calls.append(("screenshot", kind, dest_dir))
        if self._scripted.get("screenshot") is False:
            return False
        os.makedirs(dest_dir, exist_ok=True)
        name = os.path.join(dest_dir, "screenshot.png")
        with open(name, "wb") as fh:  # a real, parseable PNG so the APP surface can preview it
            fh.write(png_bytes(2, 2, bytes([26, 26, 26] * 4)))
        return name

    def capture_frame(self):
        """LOOK's fixture: scripted ("frame": (png, title, text)) or a cyclic "frames" list;
        default is a declared public gray page. Bytes on the wire only — NEVER a file here."""
        self.calls.append(("capture_frame",))
        if self._scripted.get("capture_frame") is False:
            return False
        frames = self._scripted.get("frames")
        if frames:
            idx = int(self._scripted.get("_frame_idx", 0))
            self._scripted["_frame_idx"] = idx + 1
            return frames[idx % len(frames)]
        return self._scripted.get("frame", (png_bytes(2, 2, bytes([26, 26, 26] * 4)),
                                            "Notepad", "fixture page text"))
