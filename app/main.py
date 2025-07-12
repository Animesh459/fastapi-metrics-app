import os
import asyncio
import asyncpg
import psutil
from fastapi import FastAPI, HTTPException, Request
from starlette.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from secure import SecureHeaders
from prometheus_client import generate_latest, REGISTRY

# Import your modules
from app.config import settings
from app.metrics.system_metrics import update_system_metrics
from app.middleware.metrics_middleware import MetricsMiddleware
from app.routers import api, health

secure_headers = SecureHeaders()

# FastAPI app
app = FastAPI(
    title="FastAPI PostgreSQL App",
    description="A simple FastAPI application connecting to PostgreSQL with a connection pool."
)

# Middleware: GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware: CORS (adjust allow_origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware: Logging requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

# Middleware: Secure headers (like Helmet)
@app.middleware("http")
async def secure_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    secure_headers.starlette(response)
    return response

# Custom Metrics Middleware (must be after other middlewares to capture their processing time if desired)
app.add_middleware(MetricsMiddleware)

# Database connection pool variable
db_pool = None

# Background task for updating system metrics
async def update_system_metrics_task():
    while True:
        update_system_metrics()
        await asyncio.sleep(15) # Update every 15 seconds

@app.on_event("startup")
async def startup_event():
    """
    Event handler that runs when the FastAPI application starts up.
    It initializes the PostgreSQL connection pool and starts background tasks.
    """
    global db_pool
    try:
        # Create the connection pool
        db_pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=1,
            max_size=10,
            timeout=30, # seconds to wait for a connection from the pool
            command_timeout=30 # seconds to wait for a command to execute
        )
        print(f"Successfully connected to PostgreSQL at {settings.DATABASE_URL}")

        # Pass the db_pool to routers that need it
        api.db_pool = db_pool
        health.db_pool = db_pool

        # Create a table if it doesn't exist and update gauge on startup
        async with db_pool.acquire() as connection:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                );
            """)
            print("Table 'items' checked/created successfully.")

            # Initial count for items_in_db_gauge
            count = await connection.fetchval("SELECT COUNT(*) FROM items")
            api.items_in_db_gauge.set(count)

        # Start background task for system metrics
        asyncio.create_task(update_system_metrics_task())

    except Exception as e:
        print(f"Failed to connect to PostgreSQL or create table: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Event handler that runs when the FastAPI application shuts down.
    It closes the PostgreSQL connection pool.
    """
    global db_pool
    if db_pool:
        await db_pool.close()
        print("PostgreSQL connection pool closed.")

# Include routers
app.include_router(api.router)
app.include_router(health.router)

@app.get("/")
async def read_root():
    """
    Root endpoint to verify the API is running.
    """
    return "Welcome to the FastAPI Metrics App!"

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """
    Endpoint to expose Prometheus metrics.
    """
    # This ensures the CPU utilization is updated just before metrics are exposed
    # For a more consistent view, the background task is better, but this provides fresh data on scrape.
    # update_system_metrics() # Called by background task now.
    return PlainTextResponse(generate_latest())