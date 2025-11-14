"""API endpoints"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List
from .agent.template import TemplateAgent
from config.settings import settings

router = APIRouter()
agent = TemplateAgent()


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

