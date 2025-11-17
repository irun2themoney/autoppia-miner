"""Feedback endpoint for validator results"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from api.utils.feedback_loop import FeedbackLoop

router = APIRouter()
feedback_loop = FeedbackLoop()


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
    """Record validator feedback for learning"""
    try:
        if request.success:
            feedback_loop.record_success(
                request.task_id,
                request.prompt,
                request.url,
                request.actions,
                request.score
            )
        else:
            feedback_loop.record_failure(
                request.task_id,
                request.prompt,
                request.url,
                request.actions,
                request.error
            )
        
        return JSONResponse(
            content={"status": "success", "message": "Feedback recorded"},
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )


@router.get("/feedback/stats")
async def get_feedback_stats():
    """Get feedback statistics"""
    try:
        stats = feedback_loop.get_stats()
        return JSONResponse(
            content=stats,
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )

