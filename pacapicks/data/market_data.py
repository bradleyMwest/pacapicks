import yfinance as yf

def snapshot(ticker):
    t = yf.Ticker(ticker)
    info = t.fast_info
    return {"last": info.last_price, "prev_close": info.previous_close}
