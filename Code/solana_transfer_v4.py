import sys
import json
import os
from pathlib import Path

# Acknowledge that these need to be installed. A check could be added.
try:
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.system_program import TransferParams, transfer
    from solders.transaction import Transaction
    from solana.rpc.api import Client
    from solana.rpc.types import TxOpts
except ImportError as e:
    print(json.dumps({"status": "error", "message": f"Missing required Solana library. Please run 'pip_install solana solders'. Details: {e}"}))
    sys.exit(1)

def get_rpc_url():
    return "https://api.mainnet-beta.solana.com"

def load_keypair_from_label(label: str):
    keypair_path = Path.home() / ".rickion" / "wallets" / f"{label}.json"
    if not keypair_path.exists():
        raise FileNotFoundError(f"Keypair file for '{label}' not found.")
    
    with open(keypair_path, 'r') as f:
        key_data = json.load(f) # This is a list of integers
    
    # Defensive check: ensure key_data is a list of integers
    if not isinstance(key_data, list) or not all(isinstance(i, int) for i in key_data):
        raise TypeError(f"Keypair file for '{label}' is malformed. Expected a list of integers.")
        
    return Keypair.from_bytes(bytes(key_data))

def main(from_label: str, to_address_str: str, amount_sol_str: str, mode: str):
    try:
        print(f"--- RICKION SOLANA TRANSFER (v4) ---")
        print(f"--- MODE: {mode.upper()} ---")

        # --- PRE-FLIGHT CHECKS & TYPE CASTING ---
        print("1. Validating and casting input types...")
        if not isinstance(from_label, str) or not from_label:
            return {"status": "error", "message": "from_label must be a non-empty string."}
        if not isinstance(to_address_str, str) or not to_address_str:
            return {"status": "error", "message": "to_address_str must be a non-empty string."}
        
        try:
            amount_sol_float = float(amount_sol_str)
        except (ValueError, TypeError):
            return {"status": "error", "message": f"amount_sol '{amount_sol_str}' could not be converted to a float."}
        
        print(f"  - From Label (str): {from_label}")
        print(f"  - To Address (str): {to_address_str}")
        print(f"  - Amount SOL (float): {amount_sol_float}")

        # --- SETUP ---
        print("2. Initializing Solana client and loading keypair...")
        client = Client(get_rpc_url())
        from_keypair = load_keypair_from_label(from_label)
        to_pubkey = Pubkey.from_string(to_address_str)
        print(f"  - Sender Pubkey: {from_keypair.pubkey()}")

        # --- TRANSACTION BUILDING ---
        print("3. Building transaction...")
        lamports = int(amount_sol_float * 1_000_000_000)
        print(f"  - Amount Lamports (int): {lamports}")
        
        instruction = transfer(
            TransferParams(from_pubkey=from_keypair.pubkey(), to_pubkey=to_pubkey, lamports=lamports)
        )
        recent_blockhash = client.get_latest_blockhash().value.blockhash
        transaction = Transaction.new_signed_with_payer([instruction], from_keypair.pubkey(), [from_keypair], recent_blockhash)
        print("  - Transaction built successfully.")

        # --- EXECUTION ---
        if mode == 'simulation':
            print("4. Executing transaction simulation...")
            sim_result = client.simulate_transaction(transaction, sig_verify=True)
            if sim_result.value.err:
                return {"status": "error", "mode": "simulation", "message": str(sim_result.value.err), "logs": sim_result.value.logs}
            return {"status": "success", "mode": "simulation", "message": "Transaction simulation was successful."}
        
        elif mode == 'live':
            print("4. EXECUTING LIVE TRANSACTION...")
            opts = TxOpts(skip_preflight=False, preflight_commitment="confirmed")
            tx_signature = client.send_transaction(transaction, opts=opts).value
            return {"status": "success", "mode": "live", "signature": str(tx_signature)}
        
        else:
            return {"status": "error", "message": f"Invalid mode '{mode}'."}

    except Exception as e:
        return {"status": "error", "message": f"A critical error occurred in main execution: {str(e)}"}

if __name__ == "__main__":
    # Usage: python <script> <from_label> <to_address> <amount_sol> <mode (simulation|live)>
    if len(sys.argv) != 5:
        print(json.dumps({"status": "error", "message": "Usage: python solana_transfer_v4.py <from_label> <to_address> <amount_sol> <mode>"}))
        sys.exit(1)
        
    _, from_lbl, to_addr, amount_str, run_mode = sys.argv
    
    result = main(from_lbl, to_addr, amount_str, run_mode)
    print("--- EXECUTION FINISHED ---")
    print(json.dumps(result, indent=2))