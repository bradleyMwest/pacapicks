from typing import List, Annotated, Optional
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict, computed_field

# ---------- Enums ----------


class TrendEnum(str, Enum):
    uptrend = "uptrend"
    downtrend = "downtrend"
    sideways = "sideways"
    unknown = "unknown"


class RiskToleranceEnum(str, Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"


class DecisionEnum(str, Enum):
    buy = "buy"
    hold = "hold"
    sell = "sell"
    watch = "watch"  # for “not now, monitor”


class Fundamentals(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # === GROWTH ===
    revenue_yoy_pct_q: Optional[Annotated[float, Field(ge=-100, le=1000)]] = None
    """Revenue growth (YoY) based on most recent quarter vs same quarter last year (Q/Q YoY).
    ✅ Available from yfinance (quarterly_financials).
    """

    # TODO: revenue_yoy_pct_ttm: Optional[float]
    # "TTM revenue growth (latest 4 quarters vs previous 4).
    # Requires more than 4 quarters — unreliable in yfinance, revisit with FMP paid or EDGAR API."

    # === PROFITABILITY ===
    operating_margin_pct: Optional[Annotated[float, Field(ge=-100, le=100)]] = None
    """Operating margin (latest quarter).
    ✅ Can be computed from yfinance quarterly_financials: operatingIncome / revenue.
    """

    # TODO: net_income_trend: Optional[str]
    # "Semantic label ('narrowing losses', 'swing to profit', etc.) — requires LLM + multi-quarter logic."

    # === VALUATION ===
    pe_ttm: Optional[Annotated[float, Field(ge=0)]] = None
    """Trailing P/E ratio.
    ✅ Available from yfinance.info['trailingPE'].
    """

    ps_ttm: Optional[Annotated[float, Field(ge=0)]] = None
    """Trailing P/S ratio.
    ✅ Available from yfinance.info['priceToSalesTrailing12Months'].
    """

    # TODO: pb: Optional[float]
    # "Price-to-book ratio — available from yfinance, but often unreliable."

    # === BALANCE SHEET ===
    cash_reserves_musd: Optional[Annotated[float, Field(ge=0)]] = None
    total_debt_musd: Optional[Annotated[float, Field(ge=0)]] = None

    @computed_field
    @property
    def net_debt_musd(self) -> Optional[float]:
        if self.cash_reserves_musd is None or self.total_debt_musd is None:
            return None
        return self.total_debt_musd - self.cash_reserves_musd

    """Net debt = total debt - cash.
    ✅ Both fields can be fetched from yfinance.balance_sheet (T=0 column).
    """

    # === SIZE & SCALE ===
    market_cap_musd: Optional[float] = None
    """Market cap in millions USD.
    ✅ Available from yfinance.info['marketCap'].
    """

    # TODO: revenue_ttm_musd: Optional[float]
    # "Total revenue over last 4 quarters — requires summing yfinance quarterly revenue.
    # OK for rough estimate, revisit for higher precision with better source."

    # Add warnings for any anomalies, missing data, or extreme values
    warnings: List[str] = Field(
        default_factory=list,
        description="Human-readable notes or warnings about anomalies, missing data, or extreme values",
    )


class Catalysts(BaseModel):
    next_earnings_date: Optional[date] = None
    guidance_watch_items: List[str] = Field(
        default_factory=list, description="What to listen for on earnings/guidance"
    )
    fda_or_clinical: List[str] = Field(
        default_factory=list, description="Upcoming FDA/PDUFA/trial readouts with dates"
    )
    product_launches_or_contracts: List[str] = Field(
        default_factory=list, description="New products, contracts, partnerships"
    )
    regulatory_or_legal: List[str] = Field(
        default_factory=list, description="Investigations, lawsuits, approvals"
    )
    activism_mna: List[str] = Field(
        default_factory=list, description="Activists, 13D/G, buyouts, JV, spin-offs"
    )


class Technicals(BaseModel):
    price_trend: TrendEnum = TrendEnum.unknown
    support_levels: List[Annotated[float, Field(ge=0)]] = Field(default_factory=list)
    resistance_levels: List[Annotated[float, Field(ge=0)]] = Field(default_factory=list)
    avg_daily_dollar_volume_musd: Optional[Annotated[float, Field(ge=0)]] = None
    short_interest_pct_float: Optional[Annotated[float, Field(ge=0, le=100)]] = None
    beta_1y: Optional[Annotated[float, Field(ge=-10, le=10)]] = None
    recent_move_2w_pct: Optional[Annotated[float, Field(ge=-100, le=1000)]] = Field(
        None, description="% change over last ~10 trading days"
    )
    relative_strength_note: Optional[str] = Field(
        None, description="Vs sector/benchmark; RS lines, moving averages"
    )


class MacroSector(BaseModel):
    sector: Optional[str] = None
    sector_in_favor: Optional[bool] = Field(
        None, description="Is the sector currently favored by flows/sentiment?"
    )
    competitor_perf_note: Optional[str] = Field(
        None, description="Peers’ recent results or price action"
    )
    macro_risks: List[str] = Field(
        default_factory=list,
        description="Rates, inflation, FX, geopolitics, supply chain, etc.",
    )


class PersonalFit(BaseModel):
    risk_tolerance: RiskToleranceEnum = RiskToleranceEnum.moderate
    time_horizon_days: Annotated[int, Field(ge=1)] = Field(
        30, description="Intended holding period for the thesis"
    )
    position_size_pct_of_portfolio: Optional[Annotated[float, Field(ge=0, le=100)]] = (
        None
    )
    liquidity_needs_note: Optional[str] = None
    # Exit plan (percent-based for portability across prices)
    stop_loss_pct: Optional[Annotated[float, Field(ge=0, le=100)]] = None
    profit_target_pct: Optional[Annotated[float, Field(ge=0, le=1000)]] = None


class Decision(BaseModel):
    recommendation: DecisionEnum = DecisionEnum.watch
    entry_price: Optional[Annotated[float, Field(ge=0)]] = Field(
        None, description="Preferred entry (limit) or reference price"
    )
    add_levels: List[Annotated[float, Field(ge=0)]] = Field(
        default_factory=list, description="Staggered adds on dips/breakouts"
    )
    target_price: Optional[Annotated[float, Field(ge=0)]] = None
    stop_price: Optional[Annotated[float, Field(ge=0)]] = None
    conviction_1to5: Annotated[int, Field(ge=1, le=5)] = 3
    notes: Optional[str] = Field(
        None, description="Key reasons, risks, alternative setups"
    )

    @field_validator("stop_price")
    @classmethod
    def stop_below_entry_if_both_present(cls, v, info):
        entry = info.data.get("entry_price")
        if v is not None and entry is not None and v >= entry:
            raise ValueError("stop_price should be below entry_price")
        return v

    @field_validator("target_price")
    @classmethod
    def target_above_entry_if_both_present(cls, v, info):
        entry = info.data.get("entry_price")
        if v is not None and entry is not None and v <= entry:
            raise ValueError("target_price should be above entry_price")
        return v


# ---------- Top-level ----------


class StockEvaluation(BaseModel):
    ticker: str = Field(..., description="e.g., 'CRNX'")
    as_of: date = Field(default_factory=date.today)

    fundamentals: Fundamentals = Field(default_factory=Fundamentals)
    catalysts: Catalysts = Field(default_factory=Catalysts)
    technicals: Technicals = Field(default_factory=Technicals)
    macro_sector: MacroSector = Field(default_factory=MacroSector)
    personal_fit: PersonalFit = Field(default_factory=PersonalFit)
    decision: Decision = Field(default_factory=Decision)

    quick_summary: Optional[str] = Field(
        None,
        description="One-paragraph TL;DR risk/reward and why now",
    )
