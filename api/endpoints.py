@router.get("/diagnostic/empty-actions")
async def get_empty_actions_diagnostic(task_id: Optional[str] = None):
    """
    Get diagnostic report for empty actions issues
    
    Query params:
        task_id: Optional task ID to filter by
    """
    try:
        from api.utils.empty_actions_diagnostic import get_diagnostic
        diagnostic = get_diagnostic()
        report = diagnostic.get_diagnostic_report(task_id=task_id)
        return JSONResponse(content=report, status_code=200)
    except ImportError:
        return JSONResponse(
            content={"error": "Diagnostic system not available"},
            status_code=503
        )
    except Exception as e:
        logger.error(f"Error getting diagnostic report: {e}", exc_info=True)
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
