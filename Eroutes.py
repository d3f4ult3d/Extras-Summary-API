"""
extras_routes.py — Extras breakdown route.
GET /api/v1/innings/{innings_id}/extras
"""
from fastapi import APIRouter, HTTPException, Path, status
from Emodels import ExtrasBreakdownResponse
from Eservices import ExtrasService, InningsNotFoundError

router = APIRouter()

@router.get("/innings/{innings_id}/extras", response_model=ExtrasBreakdownResponse, summary="Extras breakdown for an innings")
def get_extras_breakdown(innings_id: int = Path(..., gt=0)):
    try:
        return ExtrasService().get_extras_breakdown(innings_id)
    except InningsNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Innings '{innings_id}' not found.")
