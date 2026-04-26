import sys
import json
from pathlib import Path

try:
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
except ImportError as e:
    print(json.dumps({"status": "error", "message": f"Missing required Solana library. Details: {e}"}))
    sys.exit(1)

def load_keypair_from_label(label: str):
    keypair_path = Path.home() / ".rickion" / "wallets" / f"{label}.json"
    if not keypair_path.exists():
        raise FileNotFoundError(f"Keypair file for '{label}' not found at {keypair_path}")
    
    with open(keypair_path, 'r') as f:
        key_data = json.load(f) # This is a list of integers
    
    if not isinstance(key_data, list) or not all(isinstance(i, int) for i in key_data):
        raise TypeError(f"Keypair file for '{label}' is malformed. Expected a list of integers.")
        
    return Keypair.from_bytes(bytes(key_data))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"status": "error", "message": "Usage: python solana_diagnose_keypair.py <label>"}))
        sys.exit(1)
    
    label = sys.argv[1]
    
    try:
        keypair = load_keypair_from_label(label)
        print(json.dumps({"status": "success", "label": label, "pubkey": str(keypair.pubkey())}, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, indent=2))
