import sys
import subprocess
import os
import json

# --- CONFIGURATION ---
# The absolute path to solana.exe. This will be found and substituted.
SOLANA_EXECUTABLE_PATH = "C:\\Users\\Tomi Laine\\.local\\share\\solana\\install\\active_release\\bin\\solana.exe"
KEYPAIR_BASE_DIR = os.path.expanduser("~/.rickion/wallets")
RPC_URL = "https://api.mainnet-beta.solana.com"

def transfer_sol(from_wallet_label, to_address, amount_sol, mode='simulation'):
    """
    Transfers SOL in either 'simulation' (--dry-run) or 'live' mode.
    """
    if mode not in ['simulation', 'live']:
        return {"status": "error", "message": "Invalid mode specified. Use 'simulation' or 'live'."}

    if not os.path.exists(SOLANA_EXECUTABLE_PATH):
        return {"status": "error", "message": f"Solana executable not found at: {SOLANA_EXECUTABLE_PATH}"}

    from_keypair_path = os.path.join(KEYPAIR_BASE_DIR, f"{from_wallet_label}.json")
    if not os.path.exists(from_keypair_path):
        return {"status": "error", "message": f"Keypair file not found for label: {from_wallet_label}"}

    command = [
        SOLANA_EXECUTABLE_PATH,
        "transfer",
        "--from", from_keypair_path,
        to_address,
        str(amount_sol),
        "--url", RPC_URL,
        "--fee-payer", from_keypair_path,
        "--output", "json"
    ]

    if mode == 'simulation':
        command.append("--dry-run")

    print(f"Executing command: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=120)
        
        if mode == 'simulation':
            # Successful dry run doesn't return a signature, but indicates success.
            return {"status": "success", "mode": "simulation", "message": "Dry run validation successful."}
        else:
            # Successful live run returns a signature.
            output_json = json.loads(result.stdout)
            return {"status": "success", "mode": "live", "signature": output_json.get('signature')}

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else e.stdout.strip()
        return {"status": "error", "mode": mode, "message": f"Solana CLI Error: {error_message}"}
    except Exception as e:
        return {"status": "error", "mode": mode, "message": f"An unexpected script error occurred: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(json.dumps({"status": "error", "message": "Usage: python solana_transfer_v2.py <from_label> <to_address> <amount_sol> <mode>"}))
        sys.exit(1)
    
    from_label, to_addr, amount, run_mode = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    
    output = transfer_sol(from_label, to_addr, amount, run_mode)
    print(json.dumps(output))