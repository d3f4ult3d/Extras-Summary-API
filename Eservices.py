"""
extras_service.py — Business logic for the extras breakdown endpoint.

Layout
------
  _fetch_innings        DB stub — fetches innings context (teams, number).
  _fetch_ball_events    DB stub — fetches every ball event for the innings.
  _calc_extras          Pure helper — single pass over ball events, no DB.
  get_extras_breakdown  Public entry point called by extras_routes.py.

Key design decision
-------------------
Every count is derived from the extra_type and extras fields on ball_events.
The extras field holds the number of extra runs on that delivery (not just 1),
so a wide that runs to the boundary correctly contributes 5 to wides, not 1.
"""
from __future__ import annotations

from typing import Any, Dict, List

from Emodels import ExtrasBreakdownResponse


class InningsNotFoundError(Exception):
    """Raised when innings_id does not exist in the database."""


class ExtrasService:

    def __init__(self, db: Any) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def get_extras_breakdown(self, innings_id: int) -> ExtrasBreakdownResponse:
        """
        Build and return the extras breakdown for innings_id.
        Raises InningsNotFoundError if the innings does not exist.
        """
        innings     = await self._fetch_innings(innings_id)
        ball_events = await self._fetch_ball_events(innings_id)
        breakdown   = self._calc_extras(ball_events)

        return ExtrasBreakdownResponse(
            innings_id     = innings_id,
            innings_number = innings["innings_number"],
            batting_team   = innings["batting_team"],
            bowling_team   = innings["bowling_team"],
            total_extras   = breakdown["total_extras"],
            wides          = breakdown["wides"],
            no_balls       = breakdown["no_balls"],
            byes           = breakdown["byes"],
            leg_byes       = breakdown["leg_byes"],
            penalties      = breakdown["penalties"],
        )

    # ------------------------------------------------------------------
    # Calculation helper (pure — no DB, fully unit-testable)
    # ------------------------------------------------------------------

    @staticmethod
    def _calc_extras(ball_events: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Single pass over ball_events to produce a full extras breakdown.

        Uses two fields per ball event:
          extra_type  — category: wide | no_ball | bye | leg_bye | penalty
          extras      — number of extra runs conceded on this delivery

        Any delivery where extras == 0 is skipped immediately.
        Unrecognised extra_type values are silently ignored so that
        unexpected data does not corrupt the totals.
        """
        wides     = 0
        no_balls  = 0
        byes      = 0
        leg_byes  = 0
        penalties = 0

        for b in ball_events:
            extra_runs = b.get("extras", 0)
            if extra_runs == 0:
                continue

            extra_type = b.get("extra_type")

            if extra_type == "wide":
                wides += extra_runs
            elif extra_type == "no_ball":
                no_balls += extra_runs
            elif extra_type == "bye":
                byes += extra_runs
            elif extra_type == "leg_bye":
                leg_byes += extra_runs
            elif extra_type == "penalty":
                penalties += extra_runs

        return {
            "wides":        wides,
            "no_balls":     no_balls,
            "byes":         byes,
            "leg_byes":     leg_byes,
            "penalties":    penalties,
            "total_extras": wides + no_balls + byes + leg_byes + penalties,
        }

    # ------------------------------------------------------------------
    # DB fetch stubs (replace each body with your real ORM/query call)
    # ------------------------------------------------------------------

    async def _fetch_innings(self, innings_id: int) -> Dict[str, Any]:
        """
        SQL:
            SELECT i.id, i.innings_number,
                   bt.name  AS batting_team,
                   bwt.name AS bowling_team
            FROM   innings i
            JOIN   teams bt  ON bt.id  = i.batting_team_id
            JOIN   teams bwt ON bwt.id = i.bowling_team_id
            WHERE  i.id = :innings_id

        Raise InningsNotFoundError if no row returned.
        """
        if innings_id == 0:
            raise InningsNotFoundError(innings_id)
        return {
            "id":             innings_id,
            "innings_number": 1,
            "batting_team":   "Mumbai Indians",
            "bowling_team":   "Chennai Super Kings",
        }

    async def _fetch_ball_events(self, innings_id: int) -> List[Dict[str, Any]]:
        """
        SQL:
            SELECT extra_type, extras
            FROM   ball_events
            WHERE  innings_id = :innings_id
            ORDER  BY over_number ASC, ball_number ASC
        """
        return [
            {"extra_type": None,      "extras": 0},
            {"extra_type": None,      "extras": 0},
            {"extra_type": "wide",    "extras": 1},
            {"extra_type": None,      "extras": 0},
            {"extra_type": "no_ball", "extras": 1},
            {"extra_type": "bye",     "extras": 2},
            {"extra_type": "leg_bye", "extras": 3},
            {"extra_type": "wide",    "extras": 5},   # wide to the boundary
            {"extra_type": "penalty", "extras": 5},
            {"extra_type": None,      "extras": 0},
        ]