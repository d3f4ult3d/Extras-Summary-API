"""
extras_service.py — Extras breakdown business logic. Reads from data.py.
"""
from __future__ import annotations
from typing import Any, Dict, List
from Wdata import BALL_EVENTS, INNINGS_BY_ID
from Emodels import ExtrasBreakdownResponse
from cricket_utils import (
    DEFAULT_TEAM_NAME,
    EXTRA_SCORE_FIELDS,
    TOTAL_EXTRAS_FIELD,
    safe_extra_type,
    safe_int,
    safe_str,
)


class InningsNotFoundError(Exception):
    pass


class ExtrasService:

    def get_extras_breakdown(self, innings_id: int) -> ExtrasBreakdownResponse:
        innings = INNINGS_BY_ID.get(innings_id)
        if not innings:
            raise InningsNotFoundError(innings_id)
        balls     = BALL_EVENTS.get(innings_id, [])
        breakdown = self._calc_extras(balls)
        return ExtrasBreakdownResponse(
            innings_id     = innings_id,
            innings_number = safe_int(innings.get("innings_number")),
            batting_team   = safe_str(innings.get("batting_team"), DEFAULT_TEAM_NAME),
            bowling_team   = safe_str(innings.get("bowling_team"), DEFAULT_TEAM_NAME),
            total_extras   = breakdown[TOTAL_EXTRAS_FIELD],
            wides          = breakdown["wides"],
            no_balls       = breakdown["no_balls"],
            byes           = breakdown["byes"],
            leg_byes       = breakdown["leg_byes"],
            penalties      = breakdown["penalties"],
        )

    @staticmethod
    def _calc_extras(balls: List[Dict[str, Any]]) -> Dict[str, int]:
        totals = {field: 0 for field in EXTRA_SCORE_FIELDS.values()}
        for b in balls:
            extra_runs = safe_int(b.get("extras"))
            if extra_runs == 0:
                continue
            field_name = EXTRA_SCORE_FIELDS.get(safe_extra_type(b))
            if field_name:
                totals[field_name] += extra_runs
        totals[TOTAL_EXTRAS_FIELD] = sum(totals.values())
        return totals
