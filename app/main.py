# app/main.py
import os
import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional # Import Optional for type hinting compatibility with Python 3.9
import psutil
# Import Prometheus client library
from prometheus_client import Counter, generate_latest, Gauge , ProcessCollector, REGISTRY
from starlette.responses import PlainTextResponse
from starlette.requests import Request
# Initialize FastAPI app
app = FastAPI(
    title="FastAPI PostgreSQL App",
    description="A simple FastAPI application connecting to PostgreSQL with a connection pool."
)

# Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

# Database connection pool variable
db_pool = None

# Pydantic model for a simple item, now only with 'name'
class Item(BaseModel):
    name: str

# Prometheus Metrics
# Counter for items created
items_created_counter = Counter(
    'items_created_total',
    'Total number of items created.'
)
# Gauge for current number of items in the database
items_in_db_gauge = Gauge(
    'items_in_database',
    'Current number of items stored in the database.'
)

# Register process metrics (includes process_cpu_seconds_total)
#ProcessCollector().register(REGISTRY)

# Custom gauge for CPU utilization percentage
cpu_utilization_gauge = Gauge(
    'process_cpu_utilization_percent',
    'Process CPU utilization percentage'
)



@app.on_event("startup")
async def startup_event():
    """
    Event handler that runs when the FastAPI application starts up.
    It initializes the PostgreSQL connection pool.
    """
    global db_pool
    try:
        # Get database URL from environment variables
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set.")

        # Create the connection pool
        # min_size: minimum number of connections to keep open
        # max_size: maximum number of connections to allow
        db_pool = await asyncpg.create_pool(
            database_url,
            min_size=1,
            max_size=10,
            timeout=30, # seconds to wait for a connection from the pool
            command_timeout=30 # seconds to wait for a command to execute
        )
        print(f"Successfully connected to PostgreSQL at {database_url}")

        # Create a table if it doesn't exist and update gauge on startup
        async with db_pool.acquire() as connection:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                );
            """)
            print("Table 'items' checked/created successfully.")

            # Moved this line inside the 'async with' block
            count = await connection.fetchval("SELECT COUNT(*) FROM items")
            items_in_db_gauge.set(count)

    except Exception as e:
        print(f"Failed to connect to PostgreSQL or create table: {e}")
        # In a real application, you might want to exit or log this more severely
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


@app.get("/")
async def read_root():
    """
    Root endpoint to verify the API is running.
    """
    return {"message": "FastAPI Metrics Monitoring System is running!"}

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """
    Endpoint to expose Prometheus metrics.
    """
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_utilization_gauge.set(cpu_percent)
    return PlainTextResponse(generate_latest())

@app.post("/data", response_model=Item)
async def create_item(item: Item):
    """
    Endpoint to create a new item in the database.
    Acquires a connection from the pool, inserts data, and releases the connection.
    Increments the items_created_total counter.
    """
    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized.")

    async with db_pool.acquire() as connection:
        try:
            await connection.execute(
                "INSERT INTO items (name) VALUES ($1)",
                item.name
            )
            items_created_counter.inc() # Increment the counter
            items_in_db_gauge.inc() # Increment the gauge
            return item
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating item: {e}")


@app.get("/data", response_model=list[Item])
async def read_items():
    """
    Endpoint to retrieve all items from the database.
    Acquires a connection from the pool, fetches data, and releases the connection.
    """
    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized.")

    async with db_pool.acquire() as connection:
        try:
            rows = await connection.fetch("SELECT name FROM items")
            # Update gauge with the current count
            items_in_db_gauge.set(len(rows))
            return [Item(name=row['name']) for row in rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading items: {e}")



