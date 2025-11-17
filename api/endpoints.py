"""API endpoints"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List
from config.settings import settings
import os

router = APIRouter()

# Initialize agent based on configuration
def get_agent():
    """Get agent instance based on settings"""
    agent_type = os.getenv("AGENT_TYPE", settings.agent_type).lower()
    
    if agent_type == "hybrid":
        from .agent.hybrid import HybridAgent
        return HybridAgent()
    elif agent_type == "chutes":
        from .agent.chutes import ChutesAgent
        return ChutesAgent()
    else:
        from .agent.template import TemplateAgent
        return TemplateAgent()

agent = get_agent()


class TaskRequest(BaseModel):
    id: str
    prompt: str
    url: str


class TaskResponse(BaseModel):
    actions: List[Dict[str, Any]]
    web_agent_id: str
    recording: str
    id: str
    task_id: str


@router.options("/solve_task")
async def solve_task_options():
    """Handle CORS preflight requests"""
    return JSONResponse(
        content={},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "600",
        }
    )


@router.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    from ..utils.metrics import metrics
    return JSONResponse(
        content=metrics.get_metrics(),
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


@router.post("/solve_task")
async def solve_task(request: TaskRequest):
    """
    Main endpoint - matches ApifiedWebAgent expectations
    Input: task.clean_task() format
    Output: {actions: [], web_agent_id: str, recording: str}
    """
    try:
        # Solve task using agent
        actions = await agent.solve_task(
            task_id=request.id,
            prompt=request.prompt,
            url=request.url
        )
        
        return JSONResponse(
            content={
                "actions": actions,
                "web_agent_id": request.id,
                "recording": "",
                "id": request.id,
                "task_id": request.id,
            },
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    except Exception as e:
        # Record error in metrics
        from ..utils.metrics import metrics
        import time
        metrics.record_request(success=False, response_time=0.0, task_type="error")
        
        # Return empty actions on error (playground expects this)
        return JSONResponse(
            content={
                "actions": [],
                "web_agent_id": request.id,
                "recording": "",
                "id": request.id,
                "task_id": request.id,
            },
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )

