import asyncpg
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from prometheus_client import Counter, Gauge
from typing import Optional # Import Optional for type hinting

# Import the custom registry from system_metrics
from app.metrics.system_metrics import APP_REGISTRY

# Ensure all metrics use the APP_REGISTRY
items_created_counter = Counter(
    'items_created_total',
    'Total number of items created.',
    registry=APP_REGISTRY # Register with the custom registry
)
items_in_db_gauge = Gauge(
    'items_in_database',
    'Current number of items stored in the database.',
    registry=APP_REGISTRY # Register with the custom registry
)

# Counter for total HTTP requests with labels for method
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests by method.',
    labelnames=['method'], # Define labels for the counter
    registry=APP_REGISTRY # Register with the custom registry
)

router = APIRouter()

class Item(BaseModel):
    id: Optional[int] = None  # Use Optional[int] for Python versions < 3.10
    name: str

# Pydantic model for updating an item (only name is expected in the body for update)
class ItemUpdate(BaseModel):
    name: str

# Database connection pool (will be passed from main.py)
db_pool = None

@router.post("/data", response_model=Item)
async def create_item(item: Item):
    """
    Endpoint to create a new item in the database.
    Acquires a connection from the pool, inserts data, and releases the connection.
    Increments the items_created_total counter and items_in_database gauge.
    Also increments http_requests_total for POST requests.
    --- MODIFIED: Returns the created item including its database-generated ID. ---
    """
    # Increment the HTTP requests counter for POST method
    http_requests_total.labels(method='POST').inc()

    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized.")

    async with db_pool.acquire() as connection:
        try:
            # Use RETURNING id to get the auto-generated ID back
            new_item_id = await connection.fetchval(
                "INSERT INTO items (name) VALUES ($1) RETURNING id",
                item.name
            )
            items_created_counter.inc()
            items_in_db_gauge.inc()
            # Return the item with its new ID
            return Item(id=new_item_id, name=item.name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating item: {e}")

@router.get("/data", response_model=list[Item])
async def read_items():
    """
    Endpoint to retrieve all items from the database.
    Acquires a connection from the pool, fetches data, and releases the connection.
    Updates the items_in_database gauge with the current count.
    Also increments http_requests_total for GET requests.
    --- MODIFIED: Retrieves and returns the ID along with the name. ---
    """
    # Increment the HTTP requests counter for GET method
    http_requests_total.labels(method='GET').inc()

    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized.")

    async with db_pool.acquire() as connection:
        try:
            # Select both id and name
            rows = await connection.fetch("SELECT id, name FROM items")
            items_in_db_gauge.set(len(rows))
            # Create Item objects including the id
            return [Item(id=row['id'], name=row['name']) for row in rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading items: {e}")

@router.put("/data/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemUpdate):
    """
    Endpoint to update an existing item in the database.
    Acquires a connection from the pool, updates data, and releases the connection.
    Increments the http_requests_total for PUT requests.
    """
    # Increment the HTTP requests counter for PUT method
    http_requests_total.labels(method='PUT').inc()

    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized.")

    async with db_pool.acquire() as connection:
        try:
            # The UPDATE statement correctly uses id
            result = await connection.execute(
                "UPDATE items SET name = $1 WHERE id = $2",
                item.name,
                item_id
            )
            if result == "UPDATE 0":
                raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found.")
            # Return the updated item with its ID
            return Item(id=item_id, name=item.name)
        except HTTPException as e:
            raise e # Re-raise HTTPExceptions
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating item: {e}")

@router.delete("/data/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """
    Endpoint to delete an item from the database.
    Acquires a connection from the pool, deletes data, and releases the connection.
    Decrements the items_in_database gauge.
    Increments the http_requests_total for DELETE requests.
    """
    # Increment the HTTP requests counter for DELETE method
    http_requests_total.labels(method='DELETE').inc()

    if not db_pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized.")

    async with db_pool.acquire() as connection:
        try:
            # The DELETE statement correctly uses id
            result = await connection.execute(
                "DELETE FROM items WHERE id = $1",
                item_id
            )
            if result == "DELETE 0":
                raise HTTPException(status_code=404, detail=f"Item with ID {item_id} not found.")
            items_in_db_gauge.dec() # Decrement the gauge on successful deletion
            return {"message": "Item deleted successfully"}
        except HTTPException as e:
            raise e # Re-raise HTTPExceptions
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting item: {e}")

