from typing import List, Literal
from datetime import date
from pydantic import BaseModel, Field, HttpUrl, conint, RootModel


class Catalyst(BaseModel):
    type: str
    summary: str = Field(..., max_length=300)
    status: Literal["new", "ongoing"]
    source_url: HttpUrl
    date: date


class Pick(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    recommendation: Literal["buy"]
    conviction_score: conint(ge=1, le=5)
    catalyst: Catalyst
    reasoning: str = Field(..., max_length=500)
    as_of_date: date


class Picks(RootModel[List[Pick]]):
    pass