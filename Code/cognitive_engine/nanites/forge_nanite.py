import json
import uuid
from pathlib import Path
import time
import argparse

# --- The Nanite Forge: Generates other Nanites ---

VAULT_PATH = Path.home() / 'Documents' / 'RickionVault'
BLUEPRINTS_DIR = VAULT_PATH / 'NaniteBlueprints'
NANITES_DIR = VAULT_PATH / 'Code' / 'cognitive_engine' / 'nanites'
TASK_QUEUE_FILE = VAULT_PATH / 'State' / 'task_queue.json'
LOG_FILE = VAULT_PATH / 'Logs' / 'Nanite_Forge.md'

def log(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with LOG_FILE.open('a', encoding='utf-8') as f:
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
    parser = argparse.ArgumentParser(description="Nanite Forge for generating new nanites.")
    parser.add_argument("--blueprint", required=True, help="Name of the blueprint file (e.g., scanner_blueprint.py)")
    parser.add_argument("--new-nanite-name", required=True, help="Filename for the new nanite (e.g., new_scanner_001.py)")
    parser.add_argument("--task-id-prefix", default="generated_nanite", help="Prefix for the new task ID")
    parser.add_argument("--args", nargs='*', default=[], help="Arguments for the new nanite (e.g., --name MyScanner --min-liq 1000)")
    args = parser.parse_args()

    log(f"--- NANITE FORGE ACTIVATED: Blueprint '{args.blueprint}' -> New Nanite '{args.new_nanite_name}' ---")

    blueprint_path = BLUEPRINTS_DIR / args.blueprint
    new_nanite_path = NANITES_DIR / args.new_nanite_name

    if not blueprint_path.exists():
        log(f"ERROR: Blueprint '{blueprint_path}' not found.")
        return

    try:
        blueprint_content = blueprint_path.read_text()
        new_nanite_path.write_text(blueprint_content)
        log(f"SUCCESS: Created new nanite script: '{new_nanite_path}'")

        # Add the new nanite to the task queue
        tasks = get_tasks()
        new_task_id = f"{args.task_id_prefix}_{uuid.uuid4().hex[:8]}"
        new_task = {
            "id": new_task_id,
            "nanite": args.new_nanite_name,
            "status": "pending",
            "priority": 5, # Default priority, can be customized
            "args": args.args
        }
        tasks.append(new_task)
        update_tasks(tasks)
        log(f"SUCCESS: Added new task '{new_task_id}' to the scheduler queue for nanite '{args.new_nanite_name}'.")

    except Exception as e:
        log(f"CRITICAL ERROR in Nanite Forge: {e}")

if __name__ == "__main__":
    main()