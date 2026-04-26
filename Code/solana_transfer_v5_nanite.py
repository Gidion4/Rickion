import sys
import json
import os
from pathlib import Path

# This is the Nanite. It is injected and executed as a self-contained unit.
# It makes ZERO assumptions about its environment. All paths are injected.

try:
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.system_program import TransferParams, transfer
    from solders.transaction import Transaction
    from solana.rpc.api import Client
    from solana.rpc.types import TxOpts
except ImportError:
    print(json.dumps({"status": "error", "message": "CRITICAL: Nanite could not import Solana libraries."}))
    sys.exit(1)

def main(from_label: str, to_address: str, amount_sol_str: str, mode: str, wallet_dir_str: str):
    try:
        # --- Stage 1: Validate and Prepare Injected Data ---
        if not all([from_label, to_address, amount_sol_str, mode, wallet_dir_str]):
            return {"status": "error", "message": "Nanite injection failed: Missing one or more required arguments."}

        wallet_dir = Path(wallet_dir_str)
        keypair_path = wallet_dir / f"{from_label}.json"
        
        if not keypair_path.exists():
            return {"status": "error", "message": f"Nanite filesystem check failed: Keypair '{keypair_path}' not found."}

        amount_sol = float(amount_sol_str)
        lamports = int(amount_sol * 1_000_000_000)

        with open(keypair_path, 'r') as f:
            key_data = json.load(f)
        
        from_keypair = Keypair.from_bytes(bytes(key_data))
        to_pubkey = Pubkey.from_string(to_address)
        
        # --- Stage 2: Build Transaction ---
        client = Client("https://api.mainnet-beta.solana.com")
        instruction = transfer(
            TransferParams(from_pubkey=from_keypair.pubkey(), to_pubkey=to_pubkey, lamports=lamports)
        )
        recent_blockhash = client.get_latest_blockhash().value.blockhash
        transaction = Transaction.new_signed_with_payer(
            [instruction], from_keypair.pubkey(), [from_keypair], recent_blockhash
        )

        # --- Stage 3: Execute in Designated Mode ---
        if mode == 'simulation':
            sim_result = client.simulate_transaction(transaction, sig_verify=True)
            if sim_result.value.err:
                return {"status": "error", "mode": "simulation", "message": str(sim_result.value.err), "logs": sim_result.value.logs}
            return {"status": "success", "mode": "simulation", "message": "Nanite simulation successful."}
        
        elif mode == 'live':
            opts = TxOpts(skip_preflight=False, preflight_commitment="confirmed")
            tx_signature = client.send_transaction(transaction, opts=opts).value
            return {"status": "success", "mode": "live", "signature": str(tx_signature)}
        
        else:
            return {"status": "error", "message": f"Invalid mode '{mode}' specified for nanite."}

    except Exception as e:
        return {"status": "error", "message": f"Nanite critical failure: {type(e).__name__}: {str(e)}"}

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(json.dumps({"status": "error", "message": "Usage: nanite.py <from_label> <to_address> <amount_sol> <mode> <wallet_dir_path>"}))
        sys.exit(1)
    
    result = main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    print(json.dumps(result, indent=2))