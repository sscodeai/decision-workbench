"""FastAPI backend for Decision Workbench.

Endpoints:
  GET  /                     health check
  POST /api/decide           run the full decision pipeline
  POST /api/decide/constraints     apply constraint backfill + weighted eval
  POST /api/decide/human-decision  record the human's final choice

The API never returns a winner. It returns an option-space map and asks the
human to decide.
"""

from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .engine import apply_constraints, record_human_decision, run_decision
from .models import ConstraintRequest, DecideRequest, HumanDecisionRequest

app = FastAPI(
    title="Decision Workbench API",
    description="Expand the decision-maker's cognition BEFORE they decide.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> Dict[str, str]:
    return {"status": "ok", "service": "Decision Workbench API"}


@app.post("/api/decide")
async def decide(request: DecideRequest) -> Dict[str, Any]:
    """Run the full pipeline: bias flags -> stance divergence -> probing ->
    option-space map. Returns everything; the human decides."""
    if not request.input.strip():
        raise HTTPException(status_code=400, detail="input is required")
    decision = await run_decision(request.input)
    return decision.model_dump()


@app.post("/api/decide/constraints")
async def decide_constraints(request: ConstraintRequest) -> Dict[str, Any]:
    """Apply selected real constraints and return the weighted evaluation."""
    decision = apply_constraints(request)
    if decision is None:
        raise HTTPException(status_code=404, detail="decision not found")
    return decision.model_dump()


@app.post("/api/decide/human-decision")
async def human_decision(request: HumanDecisionRequest) -> Dict[str, Any]:
    """Record the human's final decision (never auto-picked)."""
    decision = record_human_decision(request)
    if decision is None:
        raise HTTPException(status_code=404, detail="decision not found")
    return decision.model_dump()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
