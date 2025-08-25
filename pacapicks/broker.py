import requests
from pacapicks import config

def get_positions():
    r = requests.get(f"{config.ALPACA_BASE_URL}/v2/positions", headers=config.ALPACA_HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()

def place_order(symbol, qty, side, type="market", tif="day"):
    payload = {"symbol":symbol, "qty":qty, "side":side, "type":type, "time_in_force":tif}
    r = requests.post(f"{config.ALPACA_BASE_URL}/v2/orders", json=payload, headers=config.ALPACA_HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    positions = get_positions()
    print(f"Current positions: {positions}")
