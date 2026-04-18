"""
models.py — Pydantic response models for the scoreboard endpoint.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class BatterInfo(BaseModel):
    name:        str
    runs:        int
    balls:       int
    fours:       int
    sixes:       int
    strike_rate: float = Field(..., description="(runs / balls) × 100")


class BowlerInfo(BaseModel):
    name:          str
    overs:         float
    wickets:       int
    runs_conceded: int
    economy:       float = Field(..., description="runs_conceded / overs_bowled")


class ScoreboardResponse(BaseModel):
    # Match context
    match:          str = Field(..., description="'Home vs Away' label")
    match_code:     str
    venue:          str
    match_type:     str = Field(..., description="T20 | ODI | Test")

    # Innings context
    innings_number: int = Field(..., description="0 if innings not yet started")
    batting_team:   str
    bowling_team:   str

    # Live score
    score:    str   = Field(..., description="'runs/wickets', e.g. '147/3'")
    overs:    str   = Field(..., description="'completed.balls', e.g. '14.3'")
    run_rate: float = Field(..., description="Current run rate (runs per over)")

    # Key performers
    top_batter: Optional[BatterInfo] = None
    top_bowler: Optional[BowlerInfo] = None

    # Ball-by-ball feed
    recent_balls: List[str] = Field(
        ...,
        description="Last ≤12 deliveries as symbols: '1'–'6', 'W', '•', 'Wd', 'Nb'",
    )

    # Match state
    status: str = Field(..., description="scheduled | live | completed")