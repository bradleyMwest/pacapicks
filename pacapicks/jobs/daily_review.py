import json
from pacapicks import broker, market_data


def run_daily_review():
    positions = broker.get_positions()
    portfolio_summary = []

    for pos in positions:
        symbol = pos["symbol"]
        qty = float(pos["qty"])
        last_price = market_data.snapshot(symbol)["last"]

        facts = {
            "symbol": symbol,
            "qty": qty,
            "avg_entry": pos["avg_entry_price"],
            "market_price": last_price,
            "unrealized_pl": pos["unrealized_pl"],
            "pct_change_today": pos["unrealized_intraday_plpc"],
        }

        reco = ""

        portfolio_summary.append({"facts": facts, "reco": reco})

    return portfolio_summary


if __name__ == "__main__":
    review = run_daily_review()
    print(json.dumps(review, indent=2))
