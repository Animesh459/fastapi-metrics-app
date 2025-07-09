import asyncpg
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Gauge

# Assuming these are defined globally or imported from a metrics module
items_created_counter = Counter(
    'items_created_total',
    'Total number of items created.'
)
items_in_db_gauge = Gauge(
    'items_in_database',
    'Current number of items stored in the database.'
)

router = APIRouter()

# Pydantic model for a simple item
class Item(BaseModel):
    name: str

# Database connection pool (will be passed from main.py)
db_pool = None

@router.post("/data", response_model=Item)
async def create_item(item: Item):
    """
    Endpoint to create a new item in the database.
    Acquires a connection from the pool, inserts data, and releases the connection.
    Increments the items_created_total counter and items_in_database gauge.
    """
    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized.")

    async with db_pool.acquire() as connection:
        try:
            await connection.execute(
                "INSERT INTO items (name) VALUES ($1)",
                item.name
            )
            items_created_counter.inc()
            items_in_db_gauge.inc()
            return item
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating item: {e}")

@router.get("/data", response_model=list[Item])
async def read_items():
    """
    Endpoint to retrieve all items from the database.
    Acquires a connection from the pool, fetches data, and releases the connection.
    Updates the items_in_database gauge with the current count.
    """
    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized.")

    async with db_pool.acquire() as connection:
        try:
            rows = await connection.fetch("SELECT name FROM items")
            items_in_db_gauge.set(len(rows))
            return [Item(name=row['name']) for row in rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading items: {e}")