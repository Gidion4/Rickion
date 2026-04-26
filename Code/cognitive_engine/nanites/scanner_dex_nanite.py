# This is a generic nanite for scanning dexscreener.
# The Scheduler will spawn this with different arguments.

import time
import json
import requests
import argparse
from pathlib import Path

def log(log_file, message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with log_file.open('a', encoding='utf-8') as f:
        f.write(f"{timestamp} | {message}\n")

def main():
    parser = argparse.ArgumentParser(description="DexScreener Scanner Nanite")
    parser.add_argument("--name", required=True, help="Scanner name for logging")
    parser.add_argument("--min-liq", type=int, default=0)
    parser.add_argument("--max-liq", type=int)
    parser.add_argument("--min-age", type=int) # minutes
    parser.add_argument("--max-age", type=int) # minutes
    args = parser.parse_args()

    # Ensure this path is correct for the nanite's logging
    LOG_FILE = Path.home() / 'Documents' / 'RickionVault' / 'Logs' / f"Nanite_{args.name}.md"
    API_URL = "https://api.dexscreener.com/latest/dex/pairs/solana/usd"
    
    params = {}
    if args.min_liq: params['minLiquidity'] = args.min_liq
    if args.max_liq: params['maxLiquidity'] = args.max_liq
    if args.min_age: params['minAge'] = args.min_age
    if args.max_age: params['maxAge'] = args.max_age

    log(LOG_FILE, f"--- NANITE '{args.name}' ACTIVATED with params: {params} ---")

    while True:
        try:
            response = requests.get(API_URL, params=params)
            if response.status_code == 200:
                pairs = response.json().get('pairs', [])
                log(LOG_FILE, f"Scan found {len(pairs)} pairs matching criteria.")
                # In a real scenario, this would write findings to another state file
                # for a 'trader' nanite to pick up.
            else:
                log(LOG_FILE, f"API Error: Status {response.status_code}")
        except Exception as e:
            log(LOG_FILE, f"CRITICAL ERROR: {e}")
        
        time.sleep(180) # Scan every 3 minutes

if __name__ == "__main__":
    main()