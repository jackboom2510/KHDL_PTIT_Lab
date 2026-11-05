"""Bật UTF-8 cho stdout/stderr — bắt buộc trên Windows (code page 1252/437).

Chỉ cần `import utf8_console` ở đầu script. Không có bước này, khi in tiếng Việt trên
Windows (đặc biệt khi output bị pipe qua terminal khác) Python sẽ chết với:

    UnicodeEncodeError: 'charmap' codec can't encode character '\\u0110' in position 0

Module cũng đổi code page console của Windows sang 65001 để `cmd.exe` hiển thị đúng dấu.
"""

from __future__ import annotations

import sys


def enable_utf8() -> None:
    if sys.platform == "win32":
        try:                       # code page 65001 = UTF-8, cho cmd.exe hiển thị đúng
            import ctypes

            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
        except Exception:          # noqa: BLE001 - không phải console thật thì bỏ qua
            pass
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


enable_utf8()
