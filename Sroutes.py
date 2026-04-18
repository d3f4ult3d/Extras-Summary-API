"""
routes.py — FastAPI route for the scoreboard endpoint.

The route does three things only:
  1. Accept the request and inject the DB session.
  2. Delegate entirely to ScoreboardService.
  3. Map service exceptions to HTTP responses.

No business logic lives here.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from Smodels import ScoreboardResponse
from Sservices import MatchNotFoundError, ScoreboardService

router = APIRouter()


# ---------------------------------------------------------------------------
# DB dependency — replace with your real session factory
# ---------------------------------------------------------------------------
async def get_db():
    """
    Yield a database session.

    Example (SQLAlchemy async):
        async with AsyncSessionLocal() as session:
            yield session
    """
    yield None  # swap for real session


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.get(
    "/scoreboard/{match_code}",
    response_model=ScoreboardResponse,
    summary="Live scoreboard for a match",
    responses={
        200: {"description": "Scoreboard returned successfully"},
        404: {"description": "Match not found"},
    },
)
async def get_scoreboard(match_code: str, db=Depends(get_db)):
    """
    Returns the live (or latest) scoreboard for **match_code**.

    | State                         | Response                         |
    |-------------------------------|----------------------------------|
    | Innings in progress           | Full scoreboard                  |
    | Match exists, no innings yet  | Placeholder (innings_number = 0) |
    | match_code not found          | 404                              |
    """
    try:
        service = ScoreboardService(db)
        return await service.get_scoreboard(match_code)
    except MatchNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match '{match_code}' not found.",
        )