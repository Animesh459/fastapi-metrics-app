from fastapi import APIRouter, HTTPException
import asyncpg

router = APIRouter()

# Database connection pool (will be passed from main.py)
db_pool = None

@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Checks database connectivity.
    """
    if not db_pool:
        raise HTTPException(status_code=503, detail="Service Unavailable: Database pool not initialized.")
    try:
        async with db_pool.acquire() as connection:
            await connection.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: Database connection failed - {e}")