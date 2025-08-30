from typing import List, Literal, Annotated
from datetime import date
from pydantic import BaseModel, Field, HttpUrl, RootModel


class Position(BaseModel):
    ticker: str
    shares: float
    cost_basis: float
    current_value: float


class Portfolio(BaseModel):
    positions: List[Position]
    cash: float = 0.0


class Catalyst(BaseModel):
    type: str
    summary: str = Field(..., max_length=300)
    status: Literal["new", "ongoing"]
    source_url: HttpUrl
    date: date


class Pick(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    recommendation: Literal["buy"]
    conviction_score: Annotated[
        int,
        Field(
            strict=True,
            ge=1,
            le=5,
            description="Conviction score from 1 (low) to 5 (high)",
        ),
    ]
    catalyst: Catalyst
    reasoning: str = Field(..., max_length=500)
    as_of_date: date


class Picks(RootModel[List[Pick]]):
    pass
