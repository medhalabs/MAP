"""
Run FastAPI application.

Usage:
    # With uv (recommended)
    uv run python run.py
    # or
    uv run uvicorn api.main:app --reload
    
    # Traditional way (after activating venv)
    python run.py
    # or
    uvicorn api.main:app --reload
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

