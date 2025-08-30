import requests
from pacapicks import config


def get_account():
    r = requests.get(
        f"{config.ALPACA_BASE_URL}/v2/account",
        headers=config.ALPACA_HEADERS,
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    print(config.ALPACA_BASE_URL)
    print(get_account())
