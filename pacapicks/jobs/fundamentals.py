# ---------- Imports ----------

import yfinance as yf
from pacapicks.ai.assessment_schema import Fundamentals


def load_fundamentals_from_yfinance(ticker: str) -> Fundamentals:
    yf_ticker = yf.Ticker(ticker)
    warnings = []

    try:
        info = yf_ticker.info
    except Exception as e:
        return Fundamentals(warnings=[f"Failed to fetch yfinance info: {e}"])

    try:
        q_financials = yf_ticker.quarterly_financials.T.sort_index()
        revenue_yoy_pct_q = None
        if "Total Revenue" in q_financials.columns:
            if len(q_financials) >= 5:
                most_recent = q_financials["Total Revenue"].iloc[-1]
                year_ago = q_financials["Total Revenue"].iloc[-5]
                if year_ago != 0:
                    revenue_yoy_pct_q = 100 * (most_recent - year_ago) / year_ago
            else:
                warnings.append("Not enough quarterly revenue data for YoY calc")
        else:
            warnings.append("'Total Revenue' not found in quarterly financials")

        revenue_ttm_musd = info.get("totalRevenue")
        if revenue_ttm_musd:
            revenue_ttm_musd = revenue_ttm_musd / 1e6

        operating_margin_pct = info.get("operatingMargins")
        if operating_margin_pct is not None:
            operating_margin_pct *= 100
            if not (-100 <= operating_margin_pct <= 100):
                warnings.append(
                    f"Operating margin out of bounds: {operating_margin_pct:.2f}%"
                )
                operating_margin_pct = None

        pe_ttm = info.get("trailingPE")
        ps_ttm = info.get("priceToSalesTrailing12Months")

        cash_reserves_musd = info.get("cash")
        if cash_reserves_musd is not None:
            cash_reserves_musd /= 1e6

        total_debt_musd = info.get("totalDebt")
        if total_debt_musd is not None:
            total_debt_musd /= 1e6

        net_debt_musd = None
        if cash_reserves_musd is not None and total_debt_musd is not None:
            net_debt_musd = total_debt_musd - cash_reserves_musd

        market_cap_musd = info.get("marketCap")
        if market_cap_musd:
            market_cap_musd /= 1e6

        return Fundamentals(
            revenue_yoy_pct_q=revenue_yoy_pct_q,
            revenue_yoy_pct_ttm=None,
            operating_margin_pct=operating_margin_pct,
            pe_ttm=pe_ttm,
            ps_ttm=ps_ttm,
            cash_reserves_musd=cash_reserves_musd,
            total_debt_musd=total_debt_musd,
            net_debt_musd=net_debt_musd,
            market_cap_musd=market_cap_musd,
            revenue_ttm_musd=revenue_ttm_musd,
            warnings=warnings,
        )

    except Exception as e:
        return Fundamentals(warnings=[f"Error processing yfinance data: {e}"])
