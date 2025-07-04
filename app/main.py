from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Dummy in-memory database
items = []

class Item(BaseModel):
    id: int
    name: str
    description: str = ""

@app.get("/data", response_model=List[Item])
def get_items():
    return items

@app.post("/data", response_model=Item)
def create_item(item: Item):
    items.append(item)
    return item

@app.put("/data/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item):
    for index, item in enumerate(items):
        if item.id == item_id:
            items[index] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Data not found")

@app.delete("/data/{item_id}")
def delete_item(item_id: int):
    for index, item in enumerate(items):
        if item.id == item_id:
            del items[index]
            return {"message": "Data deleted"}
    raise HTTPException(status_code=404, detail="Data not found")
