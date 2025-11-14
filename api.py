"""
Legacy API file - redirects to new modular structure
This file is kept for backward compatibility during migration
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from new structure
from api.server import app

# For backward compatibility
if __name__ == "__main__":
    import uvicorn
    from config.settings import settings
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )
