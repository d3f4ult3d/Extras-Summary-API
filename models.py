"""
extras_models.py — Pydantic models for the extras breakdown endpoint.
"""
from pydantic import BaseModel, Field


class ExtrasBreakdownResponse(BaseModel):
    """
    Clean extras breakdown for an innings.
    All counts are derived from the extra_type and extras fields on ball_events.
    Nothing is read from pre-saved summary fields.
    """
    innings_id:     int
    innings_number: int
    batting_team:   str
    bowling_team:   str

    total_extras: int = Field(..., description="Sum of all extra runs conceded")
    wides:        int = Field(..., description="Runs conceded from wide deliveries")
    no_balls:     int = Field(..., description="Runs conceded from no-ball deliveries")
    byes:         int = Field(..., description="Runs scored off byes — ball missed bat and keeper, not a wide/no-ball")
    leg_byes:     int = Field(..., description="Runs scored off the body, not the bat")
    penalties:    int = Field(..., description="Umpire-awarded penalty runs (e.g. ball-tampering, fielding violations)")