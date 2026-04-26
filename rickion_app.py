"""
================================================================
RICKION — Desktop App launcher
================================================================
Opens Rickion in its own native window (no browser chrome),
and keeps the Core running in the background.

When you double-click the "Rickion" icon on your desktop, this
file is what runs.

Requires: pywebview  (installed by requirements.txt)
"""
from __future__ import annotations

# ============================================================
# UTF-8 STDIO HARDENING — must run before ANY print()
# Windows default console is cp1252 which crashes on emojis,
# arrows, and Finnish letters. Force UTF-8 on stdout/stderr.
# ============================================================
import sys, os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
try: sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass

import pathlib
import subprocess
import threading
import time

HERE = pathlib.Path(__file__).parent.resolve()
CORE = HERE / "rickion_core.py"
UI = HERE / "rickion_command_center.html"
LOG = pathlib.Path.home() / ".rickion" / "app.log"
LOG.parent.mkdir(parents=True, exist_ok=True)


def _log(msg: str):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}\n"
    try:
        LOG.open("a", encoding="utf-8").write(line)
    except Exception:
        pass
    print(line, end="")


def _spawn_core_proc():
    """Single Core spawn attempt. Returns the subprocess.Popen handle."""
    child_env = dict(os.environ)
    child_env["PYTHONUTF8"] = "1"
    child_env["PYTHONIOENCODING"] = "utf-8"
    kwargs = dict(
        cwd=str(HERE),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=child_env,
    )
    if sys.platform.startswith("win"):
        CREATE_NO_WINDOW = 0x08000000
        kwargs["creationflags"] = CREATE_NO_WINDOW
    return subprocess.Popen([sys.executable, "-X", "utf8", str(CORE)], **kwargs)


def _start_core_in_background():
    """PHOENIX PROTOCOL — spawn rickion_core.py and KEEP it alive.

    A daemon thread watches the Core process. If it dies for any reason
    (crash, OOM, accidental kill), the watchdog respawns it automatically.

    User never has to manually restart the Core."""
    try:
        import socket
        with socket.create_connection(("127.0.0.1", 8777), timeout=0.4):
            _log("Core already listening on 127.0.0.1:8777 — skipping spawn.")
            return
    except Exception:
        pass

    def watchdog():
        backoff = 2
        max_backoff = 60
        consecutive_fails = 0
        while True:
            try:
                proc = _spawn_core_proc()
                _log(f"Core spawned (pid={proc.pid}).")
                start = time.time()
                rc = proc.wait()
                lifetime = time.time() - start
                _log(f"Core exited (code={rc}) after {lifetime:.1f}s.")
                # If it died fast, increase backoff. If it lived long, reset.
                if lifetime < 5:
                    consecutive_fails += 1
                    backoff = min(max_backoff, backoff * 2)
                else:
                    consecutive_fails = 0
                    backoff = 2
                if consecutive_fails >= 5:
                    _log(f"Core failing repeatedly. Backing off {backoff}s. Check ~/.rickion/app.log.")
                _log(f"Watchdog respawning Core in {backoff}s...")
                time.sleep(backoff)
            except Exception as e:
                _log(f"Watchdog error: {e} — sleeping 5s.")
                time.sleep(5)

    t = threading.Thread(target=watchdog, daemon=True, name="core-watchdog")
    t.start()
    _log("Core watchdog started (Phoenix Protocol).")


def main():
    # Stable persistent storage directory — localStorage survives reinstalls
    PERSIST_DIR = pathlib.Path.home() / ".rickion" / "webview"
    PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    try:
        import webview  # type: ignore
    except ImportError:
        print("pywebview missing. Install:\n    pip install pywebview")
        import webbrowser
        webbrowser.open(UI.as_uri())
        _start_core_in_background()
        time.sleep(5)
        return

    # Background: start Core
    threading.Thread(target=_start_core_in_background, daemon=True).start()

    # Foreground: native window
    window = webview.create_window(
        "RICKION",
        str(UI),
        width=1680,
        height=1020,
        min_size=(1200, 760),
        resizable=True,
        fullscreen=False,
        background_color="#030609",
        text_select=True,
    )

    gui_pref = None
    if sys.platform.startswith("win"):
        gui_pref = "edgechromium"
    elif sys.platform == "darwin":
        gui_pref = "cocoa"
    else:
        gui_pref = "gtk"

    # private_mode=False + stable storage_path = localStorage persists forever
    start_kwargs = {
        "gui": gui_pref,
        "debug": False,
        "http_server": False,
        "private_mode": False,
        "storage_path": str(PERSIST_DIR),
    }
    try:
        webview.start(**start_kwargs)
    except TypeError:
        # Older pywebview without these kwargs
        try:
            webview.start(gui=gui_pref, debug=False, http_server=False, private_mode=False)
        except Exception:
            webview.start(debug=False)
    except Exception as e:
        _log(f"webview fallback: {e}")
        webview.start(debug=False)


if __name__ == "__main__":
    main()
