from fastapi import FastAPI,Query
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import Categories,Inventory,Sales,Inventory_Changes
from dotenv import load_dotenv
import os
import uvicorn
from datetime import date,datetime,timedelta

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
        return db
    finally:
        db.close()

def calculate_revenue(db , start_date: datetime, end_date: datetime):
    if db:
        sales = db.query(Sales).filter(Sales.timestamp >= start_date, Sales.timestamp <= end_date).all()
        total_revenue = sum(sale.price_per_quantity * sale.quantity_sold for sale in sales)
        return total_revenue
    else:
        JSONResponse(content="Connection closed!",
                    status_code=504)

@app.get("/sales/filter")
async def retrieve_sales(sale_id: int = Query(None),
                         inventory_id: int = Query(None),
                         category_id:int = Query(None)):
    db = get_db()
    sale_list = []
    if db:
        if (not sale_id and not inventory_id and not category_id):
            return JSONResponse(content="Atleast one query param is required.",
                                status_code=400)
        if sale_id is not None:
            sale = db.query(Sales).filter(Sales.sale_id == sale_id).first()
            sale_list.append(sale)
            if sale is None:
                content = {"message": f'Sale with id {sale_id} doesnot exist'}
                return JSONResponse(content=content,
                                    status_code=404)
            else:
                return sale_list
            
        if inventory_id is not None:
            sale = db.query(Sales).filter(Sales.inv_id == inventory_id).all()
            sale_list.extend(sale)
            if sale_list == []:
                content = {"message": f'Inventory with id {inventory_id} wasnot sold'}
                return JSONResponse(content=content,
                                    status_code=404)
            else:
                return sale_list
        
        if category_id is not None:
            inventory = db.query(Inventory).filter(Inventory.cat_id == category_id).all()
            for inv in inventory:
                sale = db.query(Sales).filter(Sales.inv_id == inv.inv_id).all() 
                sale_list.extend(sale)

            if sale_list == []:
                content = {"message": f'Inventory with id {inventory_id} wasnot sold'}
                return JSONResponse(content=content,
                                    status_code=404)
            else:
                return sale_list

            
        
    else:
        return "connection not established"

@app.get("/sales/revenue")
def analyze_revenue(
    start_date: date = Query(None),
    end_date: date = Query(None),
    interval: str = Query("daily")
):
    db = get_db()
    if (not start_date or not end_date) or (not start_date and not end_date):
        return JSONResponse(content="Both start_date and end_date are required.",
                            status_code=400)
    if interval == "weekly":
        start_date = start_date - timedelta(days=start_date.weekday())
        end_date = start_date + timedelta(days=6)

    elif interval == "monthly":
        start_date = start_date.replace(day=1)
        end_date = start_date.replace(day=1, month=start_date.month + 1) - timedelta(days=1)

    elif interval == "annual":
        start_date = start_date.replace(month=1, day=1)
        end_date = start_date.replace(month=12, day=31)

    total_revenue = calculate_revenue(db, start_date, end_date)
    return {
        "message": f"Revenue analysis for {interval} period",
        "start_date": start_date,
        "end_date": end_date,
        "total_revenue": total_revenue
    }




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")