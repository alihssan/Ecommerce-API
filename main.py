from fastapi import FastAPI, HTTPException
from databases import Database


app = FastAPI()

DATABASE_URL = "mysql+mysqlconnector://username:password@localhost/db_name"

database = Database(DATABASE_URL)

@app.post("/items/")
async def create_item(item: Item):
    query = "INSERT INTO items (name, description) VALUES (:name, :description)"
    values = {"name": item.name, "description": item.description}
    await database.execute(query=query, values=values)
    return {"item": item}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    query = "SELECT name, description FROM items WHERE id = :id"
    values = {"id": item_id}
    result = await database.fetch_one(query=query, values=values)
    if result is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return result


