"""
extras_service.py — Extras breakdown business logic. Reads from data.py.
"""
from __future__ import annotations
from typing import Any, Dict, List
from Wdata import BALL_EVENTS, INNINGS_BY_ID
from Emodels import ExtrasBreakdownResponse
from cricket_utils import safe_extra_type, safe_int, safe_str


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
            batting_team   = safe_str(innings.get("batting_team"), "TBD"),
            bowling_team   = safe_str(innings.get("bowling_team"), "TBD"),
            total_extras   = breakdown["total_extras"],
            wides          = breakdown["wides"],
            no_balls       = breakdown["no_balls"],
            byes           = breakdown["byes"],
            leg_byes       = breakdown["leg_byes"],
            penalties      = breakdown["penalties"],
        )

    @staticmethod
    def _calc_extras(balls: List[Dict[str, Any]]) -> Dict[str, int]:
        wides = no_balls = byes = leg_byes = penalties = 0
        for b in balls:
            extra_runs = safe_int(b.get("extras"))
            if extra_runs == 0:
                continue
            t = safe_extra_type(b)
            if t == "wide":
                wides += extra_runs
            elif t == "no_ball":
                no_balls += extra_runs
            elif t == "bye":
                byes += extra_runs
            elif t == "leg_bye":
                leg_byes += extra_runs
            elif t == "penalty":
                penalties += extra_runs
        return {
            "wides": wides, "no_balls": no_balls, "byes": byes,
            "leg_byes": leg_byes, "penalties": penalties,
            "total_extras": wides + no_balls + byes + leg_byes + penalties,
        }
