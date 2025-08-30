from typing import List, Annotated, Optional
from datetime import date
from enum import Enum
from pydantic import BaseModel, Field, field_validator

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


# ---------- Sections ----------
# Annotated[float, Field(strict=True, gt=0)]


class Fundamentals(BaseModel):
    revenue_yoy_pct: Optional[Annotated[float, Field(ge=-100, le=1000)]] = Field(
        None, description="Revenue growth YoY in % (e.g., 15.2)"
    )

    revenue_qoq_pct: Optional[Annotated[float, Field(ge=-100, le=1000)]] = Field(
        None, description="Revenue growth QoQ in %"
    )
    net_income_trend: Optional[str] = Field(
        None, description="Brief note, e.g., 'narrowing losses', 'swing to profit'"
    )
    gross_margin_pct: Optional[Annotated[float, Field(ge=0, le=100)]] = None
    operating_margin_pct: Optional[Annotated[float, Field(ge=-100, le=100)]] = None
    free_cash_flow_notes: Optional[str] = Field(
        None, description="Direction/consistency of FCF; burn rate if negative"
    )
    cash_reserves_musd: Optional[Annotated[float, Field(ge=0)]] = None
    total_debt_musd: Optional[Annotated[float, Field(ge=0)]] = None

    # Valuation
    pe_ttm: Optional[Annotated[float, Field(ge=0)]] = None
    ps_ttm: Optional[Annotated[float, Field(ge=0)]] = None
    pb: Optional[Annotated[float, Field(ge=0)]] = None
    peer_valuation_note: Optional[str] = Field(
        None, description="Cheap/expensive vs peers; rationale"
    )

    insider_activity_note: Optional[str] = Field(
        None, description="Notable insider buys/sells with dates/sizes"
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
