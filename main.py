"""
Match Scoreboard API — Entry Point
Run: uvicorn main:app --reload
"""
from fastapi import FastAPI
from Sroutes import router as scoreboard_router
from Iroutes import router as innings_router
from Eroutes import router as extras_router

app = FastAPI(
    title="Match Scoreboard API",
    description=(
        "Live scoreboard and innings analytics. Returns frontend-ready JSON "
        "for the scoring page, live stream page, and AI agent tooling."
    ),
    version="1.0.0",
)

app.include_router(scoreboard_router, prefix="/api/v1", tags=["Scoreboard"])
app.include_router(innings_router,    prefix="/api/v1", tags=["Innings"])
app.include_router(extras_router,     prefix="/api/v1", tags=["Extras"])


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}