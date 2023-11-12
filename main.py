from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import Item
from dotenv import load_dotenv
import os

#load variables from .env here
load_dotenv()
database_url = os.getenv("DATABASE_URL")
debug_mode = os.getenv("DEBUG")

app = FastAPI()

#Database session maker
engine = create_engine(database_url)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#Session manage 
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

@app.post("/items/")
async def create_item(item: Item, db: Session = get_db()):
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.get("/items/{item_id}")
async def read_item(item_id: int, db: Session = get_db()):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
