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
                         category_id:int = Query(None),
                         start_date: date = Query(None),
                         end_date: date = Query(None)):
    db = get_db()
    sale_list = []
    if db:
        if (not sale_id and not inventory_id and not category_id and not start_date and not end_date):
            return JSONResponse(content="Atleast one query param is required.",
                                status_code=400)
        if (not start_date or not end_date):
            return JSONResponse(content="Both start_date and end_date are required.",
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
        
        if start_date and end_date:
            sales = db.query(Sales).filter(Sales.timestamp >= start_date, Sales.timestamp <= end_date).all()
            return sales
        
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

@app.get("/sales/revenue/compare")
def analyze_revenue(
    category1: int = Query(None),
    category2: int = Query(None),
    start_date1: date = Query(None),
    start_date2: date = Query(None),
    end_date1: date = Query(None),
    end_date2: date = Query(None)

):
    db = get_db()
    if (not category1 and not category2):
        if (not start_date1 or not end_date1) and (not start_date2 or not end_date2):
            return JSONResponse(content="Both start_date and end_date are required.",
                                status_code=400)
        
        total_revenue1 = calculate_revenue(db, start_date1, end_date1)
        total_revenue2 = calculate_revenue(db, start_date2, end_date2)

        if total_revenue1<total_revenue2:
            percent_increase = (total_revenue1/total_revenue2)*100 
        else: percent_increase = (total_revenue2/total_revenue1)*100

        return {
            "message": f"Revenue analysis for time duration {start_date1} - {end_date1} and {start_date2} - {end_date2}",
            "total_revenue_by_period_1": total_revenue1,
            "total_revenue_by_period_2": total_revenue2,
            "percentage_increase": f"Percentage increase {percent_increase}"
        }
    
    elif (category1 and category2):
        total_revenueA = 0
        total_revenueB = 0
        if (start_date1 or end_date1) or (start_date2 or end_date2):
            return JSONResponse(content="Both start_date and end_date are required.",
                                status_code=400)
        
        inventoryA = list(db.query(Inventory).filter(Inventory.cat_id == category1).all())
        inventoryB = list(db.query(Inventory).filter(Inventory.cat_id == category2).all())

        for inv in inventoryA:
            sales = db.query(Sales).filter(Sales.inv_id == inv.inv_id).all() 
            total_revenueA += sum(sale.price_per_quantity * sale.quantity_sold for sale in sales) 

        for inv in inventoryB:
            sales = db.query(Sales).filter(Sales.inv_id == inv.inv_id).all() 
            total_revenueB += sum(sale.price_per_quantity * sale.quantity_sold for sale in sales)  
    
        return {
            "message": f"Revenue analysis for {category1} and {category2}",
            "total_revenueA": total_revenueA,
            "total_revenueB": total_revenueB,
            "percent_inc_A_B": (total_revenueB/total_revenueA)*100
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")