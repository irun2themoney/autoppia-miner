"""FastAPI server setup"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .endpoints import router
from .endpoints_feedback import router as feedback_router
from .endpoints_dashboard import router as dashboard_router
from .endpoints_learning import router as learning_router
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="IWA Miner API",
    version="1.0.0",
    description="Infinite Web Arena Miner API - ApifiedWebAgent Pattern"
)

# Mount static files for dashboard
from fastapi.staticfiles import StaticFiles
import os
if os.path.exists("api/static"):
    app.mount("/static", StaticFiles(directory="api/static"), name="static")


# Initialize self-learning system (optional, non-blocking)
_documentation_learner = None
if settings.self_learning_enabled:
    try:
        from api.utils.documentation_learner import DocumentationLearner
        _documentation_learner = DocumentationLearner(
            enabled=settings.self_learning_enabled,
            check_interval=settings.self_learning_interval
        )
        logger.info("Self-learning system initialized (will start in background)")
    except Exception as e:
        logger.warning(f"Failed to initialize self-learning system: {e} (continuing without it)")


@app.on_event("startup")
async def startup_event():
    """Start background tasks on server startup"""
    if _documentation_learner:
        try:
            # Start background learning in a way that doesn't block
            import asyncio
            loop = asyncio.get_event_loop()
            _documentation_learner.start_background_learning()
            logger.info("Background documentation learning started")
        except Exception as e:
            logger.warning(f"Failed to start background learning: {e} (continuing without it)")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks on server shutdown"""
    if _documentation_learner:
        try:
            _documentation_learner.stop_background_learning()
            logger.info("Background documentation learning stopped")
        except Exception as e:
            logger.warning(f"Failed to stop background learning: {e}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)
app.include_router(feedback_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")  # Real-time dashboard
app.include_router(learning_router)  # Self-learning endpoints


@app.get("/health")
async def health():
    """Health check endpoint"""
    import os
    agent_type = os.getenv("AGENT_TYPE", settings.agent_type)
    
    try:
        from api.utils.metrics import metrics
        # Include basic metrics in health check
        metrics_data = metrics.get_metrics()
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "agent_type": agent_type,
            "metrics": {
                "total_requests": metrics_data["total_requests"],
                "success_rate": metrics_data["success_rate"],
                "cache_hit_rate": metrics_data["cache_hit_rate"],
                "avg_response_time": round(metrics_data["avg_response_time"], 3),
            }
        }
    except Exception as e:
        # Fallback if metrics not available
        return {
            "status": "healthy",
            "version": "1.0.0",
            "agent_type": agent_type,
        }


@app.get("/metrics")
async def metrics():
    """Metrics endpoint (Prometheus-compatible)"""
    try:
        from api.utils.metrics import metrics as metrics_instance
        metrics_data = metrics_instance.get_metrics()
        
        # Return Prometheus-style metrics
        return JSONResponse(
            content={
                "total_requests": metrics_data["total_requests"],
                "success_rate": metrics_data["success_rate"],
                "cache_hit_rate": metrics_data["cache_hit_rate"],
                "avg_response_time": round(metrics_data["avg_response_time"], 3),
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )


@app.get("/")
async def root():
    """Root endpoint for testing"""
    return JSONResponse(
        content={
            "status": "online",
            "version": "1.0.0",
            "endpoints": {
                "solve_task": "/solve_task",
                "health": "/health",
                "metrics": "/metrics",
                "dashboard": "/api/dashboard"
            }
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )

