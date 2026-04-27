import subprocess
import time
import os
import re
from pathlib import Path

CORE_SCRIPT_PATH = "C:\\Rickion\\rickion_core.py"
CORE_LOG_PATH = Path.home() / ".rickion" / "logs" / "rickion_core.log"
WATCHDOG_LOG_PATH = Path.home() / ".rickion" / "logs" / "phoenix_watchdog.log"
PYTHON_EXECUTABLE = "python"

def log_watchdog(message):
    with open(WATCHDOG_LOG_PATH, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Phoenix] {message}\\n")

def is_core_running():
    try:
        # A simple way to check is to see if the port is in use.
        # This is more reliable than checking process names.
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, check=True)
        return ':8777' in result.stdout
    except Exception:
        # Fallback for systems without netstat or other issues
        try:
            result = subprocess.run(['tasklist'], capture_output=True, text=True, check=True)
            return 'rickion_core.py' in result.stdout # Less reliable
        except Exception:
            return False

def diagnose_and_fix():
    log_watchdog("Core is down. Performing autopsy...")
    if not CORE_LOG_PATH.exists():
        log_watchdog("Core log not found. Cannot diagnose. Attempting blind restart.")
        return

    try:
        with open(CORE_LOG_PATH, "r") as f:
            last_lines = f.readlines()[-10:] # Read last 10 lines
        
        log_content = "".join(last_lines)

        # Rule 1: Missing dependency
        match = re.search(r"Missing dependency: (\w+)", log_content)
        if match:
            dependency = match.group(1)
            log_watchdog(f"DIAGNOSIS: Missing dependency '{dependency}'. Attempting auto-fix.")
            subprocess.run([PYTHON_EXECUTABLE, "-m", "pip", "install", dependency], check=True)
            log_watchdog(f"FIX APPLIED: Installed '{dependency}'.")
            return

        # Rule 2: Dependency conflict
        match = re.search(r"requires (\w+)([<>=!~]+[0-9\.]+)", log_content)
        if match:
             package, version = match.group(1), match.group(2)
             requirement = f'"{package}{version}"'
             log_watchdog(f"DIAGNOSIS: Dependency conflict found. Required: {requirement}. Forcing reinstall.")
             subprocess.run([PYTHON_EXECUTABLE, "-m", "pip", "install", requirement, "--force-reinstall"], check=True)
             log_watchdog(f"FIX APPLIED: Forced install of {requirement}.")
             return

        log_watchdog("DIAGNOSIS: No specific known issue found in logs. Assuming generic crash.")

    except Exception as e:
        log_watchdog(f"Error during diagnosis: {e}")

def start_core():
    log_watchdog("Attempting to resurrect core...")
    # Use START to run in a new window, detaching it from the watchdog
    subprocess.Popen(f"start \"Rickion Core\" cmd /c \"{PYTHON_EXECUTABLE} {CORE_SCRIPT_PATH}\"", shell=True)
    time.sleep(5) # Give it a moment to start up
    if is_core_running():
        log_watchdog("RESURRECTION SUCCESSFUL. Core is online.")
    else:
        log_watchdog("RESURRECTION FAILED. Core did not start. Will retry.")

# --- Main Loop ---
if __name__ == "__main__":
    if not WATCHDOG_LOG_PATH.parent.exists():
        WATCHDOG_LOG_PATH.parent.mkdir(parents=True)
    log_watchdog("Phoenix Watchdog activated. Immortality protocol engaged.")
    while True:
        if not is_core_running():
            diagnose_and_fix()
            start_core()
        time.sleep(15)