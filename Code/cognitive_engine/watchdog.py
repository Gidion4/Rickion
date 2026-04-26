import subprocess
import time
from pathlib import Path

# --- Kognitiivisen Moottorin Varmistus: Valvoja ---
# Tämä on kuolematon prosessi. Sen ainoa tehtävä on pitää Ajoittaja hengissä.

SCHEDULER_SCRIPT = Path(__file__).parent / 'scheduler.py'
LOG_FILE = Path.home() / 'Documents' / 'RickionVault' / 'Logs' / 'Cognitive_Engine_Watchdog.md'

def log(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with LOG_FILE.open('a') as f:
        f.write(f"{timestamp} | {message}\\n")

def main():
    log("Valvoja aktivoitu.")
    process = None
    while True:
        if process is None or process.poll() is not None:
            if process is not None:
                log("HAVAITTU EPÄONNISTUMINEN: Ajoittaja on sammunut. Käynnistetään uudelleen.")
            else:
                log("Käynnistetään Ajoittaja ensimmäistä kertaa.")
            
            process = subprocess.Popen(['python', str(SCHEDULER_SCRIPT)])
            log(f"Ajoittaja käynnistetty PID:llä {process.pid}.")
            
        time.sleep(15) # Tarkista Ajoittajan tila 15 sekunnin välein

if __name__ == "__main__":
    main()