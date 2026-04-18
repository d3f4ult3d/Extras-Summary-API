"""
service.py — All business logic for the scoreboard endpoint.

Layout
------
  _fetch_*   DB stubs. Each has the exact SQL it should run in a comment.
             Swap the stub body for a real asyncpg / SQLAlchemy call.

  _calc_*    Pure calculation helpers. No DB access, no side-effects.
             Fully unit-testable without a database.

  get_scoreboard   Public entry point called by the route.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from Smodels import BatterInfo, BowlerInfo, ScoreboardResponse


class MatchNotFoundError(Exception):
    """Raised when match_code does not exist in the database."""


class ScoreboardService:

    def __init__(self, db: Any) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def get_scoreboard(self, match_code: str) -> ScoreboardResponse:
        """
        Build and return the scoreboard for match_code.

        Raises MatchNotFoundError if the match does not exist.
        Returns a placeholder response if the match exists but no innings
        has been created yet.
        """
        match   = await self._fetch_match(match_code)
        innings = await self._fetch_active_innings(match["id"])

        if innings is None:
            return self._build_no_innings_response(match)

        batting = await self._fetch_batting_cards(innings["id"])
        bowling = await self._fetch_bowling_cards(innings["id"])
        balls   = await self._fetch_recent_balls(innings["id"], limit=12)

        return ScoreboardResponse(
            match          = f"{match['home_team']} vs {match['away_team']}",
            match_code     = match["match_code"],
            venue          = match["venue"],
            match_type     = match["match_type"],
            innings_number = innings["innings_number"],
            batting_team   = innings["batting_team"],
            bowling_team   = innings["bowling_team"],
            score          = self._calc_score(innings),
            overs          = self._calc_overs(innings["total_balls"]),
            run_rate       = self._calc_run_rate(innings["total_runs"], innings["total_balls"]),
            top_batter     = self._calc_top_batter(batting),
            top_bowler     = self._calc_top_bowler(bowling),
            recent_balls   = self._calc_ball_symbols(balls),
            status         = match["status"],
        )

    # ------------------------------------------------------------------
    # Calculation helpers (pure — no DB, fully unit-testable)
    # ------------------------------------------------------------------

    @staticmethod
    def _calc_score(innings: Dict[str, Any]) -> str:
        """Return 'runs/wickets', e.g. '147/3'."""
        return f"{innings['total_runs']}/{innings['total_wickets']}"

    @staticmethod
    def _calc_overs(total_balls: int) -> str:
        """
        Convert a raw ball count to an overs string.
        73 balls → '12.1'  |  90 balls → '15.0'
        """
        return f"{total_balls // 6}.{total_balls % 6}"

    @staticmethod
    def _calc_run_rate(total_runs: int, total_balls: int) -> float:
        """Runs per over, rounded to 2 dp. Returns 0.0 before any ball."""
        if total_balls == 0:
            return 0.0
        return round(total_runs / (total_balls / 6), 2)

    @staticmethod
    def _calc_strike_rate(runs: int, balls: int) -> float:
        if balls == 0:
            return 0.0
        return round((runs / balls) * 100, 2)

    @staticmethod
    def _calc_economy(runs_conceded: int, overs_bowled: float) -> float:
        if overs_bowled == 0:
            return 0.0
        return round(runs_conceded / overs_bowled, 2)

    @staticmethod
    def _calc_top_batter(cards: List[Dict[str, Any]]) -> Optional[BatterInfo]:
        """
        Highest run-scorer who is still not out.
        Falls back to highest scorer overall if everyone is out.
        Returns None if no batting data exists yet.
        """
        if not cards:
            return None
        active = [c for c in cards if not c["is_out"]] or cards
        best = max(active, key=lambda c: c["runs_scored"])
        return BatterInfo(
            name        = best["player_name"],
            runs        = best["runs_scored"],
            balls       = best["balls_faced"],
            fours       = best["fours"],
            sixes       = best["sixes"],
            strike_rate = ScoreboardService._calc_strike_rate(
                best["runs_scored"], best["balls_faced"]
            ),
        )

    @staticmethod
    def _calc_top_bowler(cards: List[Dict[str, Any]]) -> Optional[BowlerInfo]:
        """
        Best bowler by wickets; economy used as tie-breaker (lower is better).
        Returns None if no bowling data exists yet.
        """
        if not cards:
            return None
        best = max(
            cards,
            key=lambda c: (
                c["wickets_taken"],
                -ScoreboardService._calc_economy(
                    c["runs_conceded"], float(c["overs_bowled"])
                ),
            ),
        )
        return BowlerInfo(
            name          = best["player_name"],
            overs         = float(best["overs_bowled"]),
            wickets       = best["wickets_taken"],
            runs_conceded = best["runs_conceded"],
            economy       = ScoreboardService._calc_economy(
                best["runs_conceded"], float(best["overs_bowled"])
            ),
        )

    @staticmethod
    def _calc_ball_symbols(balls: List[Dict[str, Any]]) -> List[str]:
        """
        Map raw ball_events rows to display symbols:
          wicket     → "W"
          wide       → "Wd"
          no-ball    → "Nb"
          dot ball   → "•"
          runs 1–6   → "1" … "6"
        """
        symbols = []
        for b in balls:
            if b["is_wicket"]:
                symbols.append("W")
            elif b.get("extra_type") == "wide":
                symbols.append("Wd")
            elif b.get("extra_type") == "no_ball":
                symbols.append("Nb")
            elif b["runs_scored"] == 0:
                symbols.append("•")
            else:
                symbols.append(str(b["runs_scored"]))
        return symbols

    # ------------------------------------------------------------------
    # No-innings placeholder
    # ------------------------------------------------------------------

    @staticmethod
    def _build_no_innings_response(match: Dict[str, Any]) -> ScoreboardResponse:
        """
        Called when a match row exists but no innings row has been created yet.
        Returns a valid ScoreboardResponse with safe zero/empty values so the
        frontend can render a 'match not started' state without extra logic.
        Frontend signal: innings_number == 0
        """
        return ScoreboardResponse(
            match          = f"{match['home_team']} vs {match['away_team']}",
            match_code     = match["match_code"],
            venue          = match["venue"],
            match_type     = match["match_type"],
            innings_number = 0,
            batting_team   = "TBD",
            bowling_team   = "TBD",
            score          = "0/0",
            overs          = "0.0",
            run_rate       = 0.0,
            top_batter     = None,
            top_bowler     = None,
            recent_balls   = [],
            status         = match["status"],
        )

    # ------------------------------------------------------------------
    # DB fetch stubs (replace each body with your real ORM/query call)
    # ------------------------------------------------------------------

    async def _fetch_match(self, match_code: str) -> Dict[str, Any]:
        """
        SQL:
            SELECT m.id, m.match_code, m.match_type, m.status,
                   ht.name AS home_team,
                   at.name AS away_team,
                   v.name  AS venue
            FROM   matches m
            JOIN   teams   ht ON ht.id = m.home_team_id
            JOIN   teams   at ON at.id = m.away_team_id
            JOIN   venues  v  ON v.id  = m.venue_id
            WHERE  m.match_code = :match_code

        Raise MatchNotFoundError if no row returned.
        """
        if match_code == "NOT-FOUND":
            raise MatchNotFoundError(match_code)
        return {
            "id":         1,
            "match_code": match_code,
            "home_team":  "Mumbai Indians",
            "away_team":  "Chennai Super Kings",
            "venue":      "Wankhede Stadium, Mumbai",
            "match_type": "T20",
            "status":     "live",
        }

    async def _fetch_active_innings(self, match_id: int) -> Optional[Dict[str, Any]]:
        """
        SQL:
            SELECT i.id, i.innings_number, i.total_runs, i.total_wickets,
                   i.total_balls, i.extras, i.status,
                   bt.name  AS batting_team,
                   bwt.name AS bowling_team
            FROM   innings i
            JOIN   teams bt  ON bt.id  = i.batting_team_id
            JOIN   teams bwt ON bwt.id = i.bowling_team_id
            WHERE  i.match_id = :match_id
              AND  i.status   = 'in_progress'
            ORDER  BY i.innings_number DESC
            LIMIT  1

        Return None if no rows (match exists, innings not yet started).
        """
        return {
            "id":             1,
            "innings_number": 1,
            "batting_team":   "Mumbai Indians",
            "bowling_team":   "Chennai Super Kings",
            "total_runs":     147,
            "total_wickets":  3,
            "total_balls":    87,
            "extras":         8,
            "status":         "in_progress",
        }

    async def _fetch_batting_cards(self, innings_id: int) -> List[Dict[str, Any]]:
        """
        SQL:
            SELECT bs.runs_scored, bs.balls_faced, bs.fours, bs.sixes, bs.is_out,
                   p.name AS player_name
            FROM   batting_scorecards bs
            JOIN   players p ON p.id = bs.player_id
            WHERE  bs.innings_id = :innings_id
            ORDER  BY bs.batting_position
        """
        return [
            {"player_name": "Rohit Sharma",    "runs_scored": 72, "balls_faced": 48,
             "fours": 7, "sixes": 4, "is_out": False},
            {"player_name": "Ishan Kishan",    "runs_scored": 41, "balls_faced": 30,
             "fours": 4, "sixes": 2, "is_out": True},
            {"player_name": "Suryakumar Yadav","runs_scored": 22, "balls_faced": 14,
             "fours": 2, "sixes": 1, "is_out": False},
        ]

    async def _fetch_bowling_cards(self, innings_id: int) -> List[Dict[str, Any]]:
        """
        SQL:
            SELECT bs.overs_bowled, bs.runs_conceded, bs.wickets_taken,
                   p.name AS player_name
            FROM   bowling_scorecards bs
            JOIN   players p ON p.id = bs.player_id
            WHERE  bs.innings_id = :innings_id
        """
        return [
            {"player_name": "Deepak Chahar",  "overs_bowled": 3.0,
             "wickets_taken": 2, "runs_conceded": 24},
            {"player_name": "Ravindra Jadeja", "overs_bowled": 2.3,
             "wickets_taken": 1, "runs_conceded": 18},
        ]

    async def _fetch_recent_balls(
        self, innings_id: int, limit: int = 12
    ) -> List[Dict[str, Any]]:
        """
        SQL:
            SELECT runs_scored, extras, extra_type, is_wicket
            FROM   ball_events
            WHERE  innings_id = :innings_id
            ORDER  BY over_number ASC, ball_number ASC

        Slice the last :limit balls in Python to preserve over order.
        """
        all_balls = [
            {"runs_scored": 1, "extras": 0, "extra_type": None,   "is_wicket": False},
            {"runs_scored": 0, "extras": 0, "extra_type": None,   "is_wicket": False},
            {"runs_scored": 4, "extras": 0, "extra_type": None,   "is_wicket": False},
            {"runs_scored": 0, "extras": 1, "extra_type": "wide", "is_wicket": False},
            {"runs_scored": 6, "extras": 0, "extra_type": None,   "is_wicket": False},
            {"runs_scored": 1, "extras": 0, "extra_type": None,   "is_wicket": False},
            {"runs_scored": 0, "extras": 0, "extra_type": None,   "is_wicket": True},
            {"runs_scored": 2, "extras": 0, "extra_type": None,   "is_wicket": False},
        ]
        return all_balls[-limit:]