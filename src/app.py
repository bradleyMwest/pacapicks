import os, requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("ALPACA_BASE_URL")
KEY  = os.getenv("ALPACA_API_KEY")
SEC  = os.getenv("ALPACA_API_SECRET")
HEAD = {"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC}

def get_account():
    r = requests.get(f"{BASE}/v2/account", headers=HEAD, timeout=10)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    print(get_account())