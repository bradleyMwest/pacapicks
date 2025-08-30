import requests
from typing import Optional
from pacapicks.ai.assessment_schema import Fundamentals
from pacapicks.config import FMP_API_KEY


def fetch_fundamentals_fmp_free(ticker: str) -> Optional[Fundamentals]:
    base = "https://financialmodelingprep.com/api/v3"
    headers = {"User-Agent": "python"}

    try:
        # Income statement (quarterly)
        income_url = f"{base}/income-statement/{ticker}?period=quarter&?limit=8&apikey={FMP_API_KEY}"
        income_data = requests.get(income_url, headers=headers).json()

        # Balance sheet
        balance_url = (
            f"{base}/balance-sheet-statement/{ticker}?limit=1&apikey={FMP_API_KEY}"
        )
        balance_data = requests.get(balance_url, headers=headers).json()

        # Quote for market cap & ratios
        quote_url = f"{base}/quote/{ticker}?apikey={FMP_API_KEY}"
        quote_data = requests.get(quote_url, headers=headers).json()

        if not income_data or len(income_data) < 8:
            print(income_data)
            print("Not enough income statement data.")
            return None

        # TTM revenue
        last_4 = [q.get("revenue", 0) for q in income_data[:4]]
        prev_4 = [q.get("revenue", 0) for q in income_data[4:8]]

        if not all(last_4) or not all(prev_4):
            print("Missing revenue data.")
            return None

        revenue_ttm = sum(last_4)
        revenue_prev_ttm = sum(prev_4)
        revenue_yoy_pct_ttm = (
            100.0 * (revenue_ttm - revenue_prev_ttm) / revenue_prev_ttm
            if revenue_prev_ttm
            else None
        )

        # Operating margin (latest quarter)
        op_income = income_data[0].get("operatingIncome")
        revenue_latest = income_data[0].get("revenue")
        operating_margin_pct = (
            100.0 * op_income / revenue_latest
            if op_income is not None and revenue_latest
            else None
        )

        # Balance sheet
        balance = balance_data[0] if balance_data else {}
        cash = balance.get("cashAndCashEquivalents")
        debt = balance.get("totalDebt")

        # Quote
        quote = quote_data[0] if quote_data else {}
        market_cap = quote.get("marketCap")
        pe_ttm = quote.get("pe")
        ps_ttm = quote.get("priceToSalesTrailing12Months")

        return Fundamentals(
            revenue_yoy_pct_ttm=revenue_yoy_pct_ttm,
            revenue_ttm_musd=revenue_ttm / 1e6,
            operating_margin_pct=operating_margin_pct,
            cash_reserves_musd=cash / 1e6 if cash else None,
            total_debt_musd=debt / 1e6 if debt else None,
            market_cap_musd=market_cap / 1e6 if market_cap else None,
            pe_ttm=pe_ttm,
            ps_ttm=ps_ttm,
        )

    except Exception as e:
        print(f"Error fetching fundamentals for {ticker}: {e}")
        return None
