"""FastAPI server setup"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .endpoints import router
from config.settings import settings

app = FastAPI(
    title="IWA Miner API",
    version="1.0.0",
    description="Infinite Web Arena Miner API - ApifiedWebAgent Pattern"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


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


@app.get("/")
async def root():
    """Root endpoint for testing"""
    return JSONResponse(
        content={
            "status": "online",
            "version": "1.0.0",
            "endpoints": {
                "solve_task": "/solve_task",
                "health": "/health"
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

