"""Feedback endpoint for validator results"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
# SIMPLIFIED: Removed FeedbackLoop (not needed for simple miner)

router = APIRouter()
# SIMPLIFIED: Removed FeedbackLoop (not needed for simple miner)


class FeedbackRequest(BaseModel):
    task_id: str
    prompt: str
    url: str
    actions: List[Dict[str, Any]]
    success: bool
    score: Optional[float] = None
    error: Optional[str] = None


@router.post("/feedback")
async def record_feedback(request: FeedbackRequest):
    """Record validator feedback - SIMPLIFIED: Just acknowledge receipt"""
    # SIMPLIFIED: Removed feedback loop (not needed for simple miner)
    return JSONResponse(
        content={"status": "success", "message": "Feedback received"},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.get("/feedback/stats")
async def get_feedback_stats():
    """Get feedback statistics - SIMPLIFIED: Return empty stats"""
    # SIMPLIFIED: Removed feedback loop (not needed for simple miner)
    return JSONResponse(
        content={"status": "success", "stats": {}},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

