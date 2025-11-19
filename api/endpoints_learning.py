"""Endpoints for self-learning system"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/learning/status")
async def learning_status():
    """Get status of self-learning system"""
    try:
        from config.settings import settings
        from api.utils.documentation_learner import DocumentationLearner
        
        # Try to get the global instance if it exists
        # Otherwise create a temporary one to check status
        try:
            from api.server import _documentation_learner
            learner = _documentation_learner
        except:
            learner = DocumentationLearner(
                enabled=settings.self_learning_enabled,
                check_interval=settings.self_learning_interval
            )
        
        if learner:
            patterns = learner.get_learned_patterns()
            return JSONResponse(content={
                "enabled": learner.enabled,
                "check_interval": learner.check_interval,
                "total_patterns": len(patterns.get("patterns", {})),
                "best_practices": len(patterns.get("best_practices", [])),
                "last_updated": patterns.get("last_updated"),
                "status": "active" if learner.enabled else "disabled"
            })
        else:
            return JSONResponse(content={
                "enabled": False,
                "status": "not_initialized"
            })
    except Exception as e:
        logger.error(f"Error getting learning status: {e}")
        return JSONResponse(
            content={"error": str(e), "status": "error"},
            status_code=500
        )


@router.post("/api/learning/trigger")
async def trigger_learning():
    """Manually trigger a learning cycle"""
    try:
        from config.settings import settings
        from api.utils.documentation_learner import DocumentationLearner
        
        try:
            from api.server import _documentation_learner
            learner = _documentation_learner
        except:
            learner = DocumentationLearner(
                enabled=settings.self_learning_enabled,
                check_interval=settings.self_learning_interval
            )
        
        if learner and learner.enabled:
            result = await learner.learn_from_documentation()
            return JSONResponse(content={
                "status": "success",
                "result": result
            })
        else:
            return JSONResponse(
                content={"error": "Self-learning is disabled"},
                status_code=400
            )
    except Exception as e:
        logger.error(f"Error triggering learning: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )


@router.get("/api/learning/patterns")
async def get_learned_patterns():
    """Get all learned patterns"""
    try:
        from config.settings import settings
        from api.utils.documentation_learner import DocumentationLearner
        
        try:
            from api.server import _documentation_learner
            learner = _documentation_learner
        except:
            learner = DocumentationLearner(
                enabled=settings.self_learning_enabled,
                check_interval=settings.self_learning_interval
            )
        
        if learner:
            patterns = learner.get_learned_patterns()
            return JSONResponse(content=patterns)
        else:
            return JSONResponse(content={
                "patterns": {},
                "best_practices": [],
                "updates": [],
                "last_updated": None
            })
    except Exception as e:
        logger.error(f"Error getting learned patterns: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

