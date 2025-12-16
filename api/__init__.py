"""API module"""
from __future__ import annotations

# Avoid importing runtime web dependencies (FastAPI, etc.) at package import time.
# This keeps lightweight tooling (e.g. pytest collection, static analysis) working
# even if optional runtime dependencies are not installed in the current env.
try:
    from .server import app  # type: ignore
except ModuleNotFoundError:
    # e.g. fastapi not installed in minimal/test environments
    app = None  # type: ignore

__all__ = ["app"]

