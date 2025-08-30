import yfinance as yf


def snapshot(ticker):
    t = yf.Ticker(ticker)
    info = t.fast_info
    return {"last": info.last_price, "prev_close": info.previous_close}


if __name__ == "__main__":
    # Example usage
    print(snapshot("AAPL"))
    print(snapshot("GOOGL"))
    print(snapshot("MSFT"))
    print(snapshot("AMZN"))
    print(snapshot("TSLA"))
    print(snapshot("NFLX"))
