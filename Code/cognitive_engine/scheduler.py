import json
import subprocess
import time
from pathlib import Path

# --- Kognitiivisen Moottorin Sydän: Tehtävien Ajoittaja ---
# Tämä prosessi on jatkuvasti päällä, ja Valvoja valvoo sitä.

VAULT_PATH = Path.home() / 'Documents' / 'RickionVault'
TASK_QUEUE_FILE = VAULT_PATH / 'State' / 'task_queue.json'
LOG_FILE = VAULT_PATH / 'Logs' / 'Cognitive_Engine_Scheduler.md'
NANITE_DIR = VAULT_PATH / 'Code' / 'cognitive_engine' / 'nanites'
RUNNING_PROCESSES = {} # task_id: subprocess.Popen object

def log(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with LOG_FILE.open('a') as f:
        f.write(f"{timestamp} | {message}\\n")

def get_tasks():
    if not TASK_QUEUE_FILE.exists():
        return []
    with TASK_QUEUE_FILE.open('r') as f:
        return json.load(f)

def update_tasks(tasks):
    with TASK_QUEUE_FILE.open('w') as f:
        json.dump(tasks, f, indent=2)

def main():
    log("Ajoittaja käynnistetty.")
    NANITE_DIR.mkdir(exist_ok=True) # Varmista, että naniittihakemisto on olemassa

    while True:
        # Tarkista kuolleet prosessit
        for task_id, process in list(RUNNING_PROCESSES.items()):
            if process.poll() is not None: # Prosessi on päättynyt
                log(f"Naniitti '{task_id}' on päättänyt toimintansa.")
                del RUNNING_PROCESSES[task_id]

        # Hae uudet tehtävät
        tasks = get_tasks()
        task_to_run = None
        for task in tasks:
            if task['status'] == 'pending' and task['id'] not in RUNNING_PROCESSES:
                task_to_run = task
                break # Aja vain yksi uusi kerrallaan estääksesi ylikuormituksen

        if task_to_run:
            task_id = task_to_run['id']
            nanite_script = NANITE_DIR / task_to_run['nanite']
            args = task_to_run.get('args', [])
            
            if not nanite_script.exists():
                log(f"VIRHE: Naniittia '{task_to_run['nanite']}' ei löydy. Merkitsen epäonnistuneeksi.")
                task_to_run['status'] = 'failed'
            else:
                log(f"Käynnistetään naniitti '{task_id}' skriptillä '{nanite_script}'")
                command = ['python', str(nanite_script)] + args
                process = subprocess.Popen(command)
                RUNNING_PROCESSES[task_id] = process
                task_to_run['status'] = 'running'
            
            update_tasks(tasks)
        
        time.sleep(5) # Tarkista uudet tehtävät 5 sekunnin välein

if __name__ == "__main__":
    main()