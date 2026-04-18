"""
extras_routes.py — Route for the extras breakdown endpoint.

GET /api/v1/innings/{innings_id}/extras

Thin route — all logic lives in ExtrasService.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from Emodels import ExtrasBreakdownResponse
from Eservices import ExtrasService, InningsNotFoundError

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
    yield None


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.get(
    "/innings/{innings_id}/extras",
    response_model=ExtrasBreakdownResponse,
    summary="Extras breakdown for an innings",
    responses={
        200: {"description": "Extras breakdown returned successfully"},
        404: {"description": "Innings not found"},
    },
)
async def get_extras_breakdown(innings_id: int, db=Depends(get_db)):
    """
    Returns a clean extras breakdown for **innings_id**.

    All counts are derived from the `extra_type` and `extras` fields
    on `ball_events` — no manual summary fields are read.

    | Field        | What it counts                                      |
    |--------------|-----------------------------------------------------|
    | wides        | Runs from wide deliveries                           |
    | no_balls     | Runs from no-ball deliveries                        |
    | byes         | Runs scored without touching the bat (not a wide)   |
    | leg_byes     | Runs off the body, not the bat                      |
    | penalties    | Umpire-awarded penalty runs                         |
    | total_extras | Sum of all the above                                |
    """
    try:
        service = ExtrasService(db)
        return await service.get_extras_breakdown(innings_id)
    except InningsNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Innings '{innings_id}' not found.",
        )