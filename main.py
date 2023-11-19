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
import random

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
    """
    Calculate total revenue for a given time interval.

    Parameters:
    - db: Database session
    - start_date: Start date for the revenue calculation
    - end_date: End date for the revenue calculation

    Returns:
    - Total revenue for the specified time interval
    """
    if db:
        sales = db.query(Sales).filter(Sales.timestamp >= start_date, Sales.timestamp <= end_date).all()
        total_revenue = sum(sale.price_per_quantity * sale.quantity_sold for sale in sales)
        return total_revenue
    else:
        JSONResponse(content="Connection closed!",
                    status_code=504)


@app.get("/sales/filter")
async def retrieve_sales(sale_id: int = Query(None),inventory_id: int = Query(None),category_id:int = Query(None),start_date: date = Query(None),end_date: date = Query(None)):
    """
    Retrieve sales data based on specified filters.

    Parameters:
    - sale_id: ID of the sale to retrieve
    - inventory_id: ID of the inventory to retrieve sales for
    - category_id: ID of the category to retrieve sales for
    - start_date: Start date for the time range of sales
    - end_date: End date for the time range of sales

    Returns:
    - List of sales data matching the specified filters
    """
    
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
def analyze_revenue(start_date: date = Query(None),
                    end_date: date = Query(None),
                    interval: str = Query("daily")):
    """
    Analyze revenue for a specified time interval.

    Parameters:
    - start_date: Start date for the revenue analysis
    - end_date: End date for the revenue analysis
    - interval: Time interval for analysis (daily, weekly, monthly, annual)

    Returns:
    - Revenue analysis results
    """
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
    """
    Compare revenue between two categories for specified time intervals.

    Parameters:
    - category1: ID of the first category
    - category2: ID of the second category
    - start_date1: Start date for the time range of the first category
    - start_date2: Start date for the time range of the second category
    - end_date1: End date for the time range of the first category
    - end_date2: End date for the time range of the second category

    Returns:
    - Revenue comparison results
    """
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

@app.get("/inventory/status")
def analyze_revenue(
    inv_id: int = Query(None),
    cat_id: int = Query(None)
):
    """
    Retrieve inventory status based on specified filters.

    Parameters:
    - inv_id: ID of the inventory
    - cat_id: ID of the category

    Returns:
    - Inventory status information
    """
    db = get_db()
    if (not inv_id and not cat_id):
        return JSONResponse(content="Atleast inv_id or cat_id is required.",
                            status_code=400)
    
    inventory = db.query(Inventory).filter(Inventory.inv_id == inv_id).first()
    content = {
        "current_stock": inventory.current_stock,
        "low_stock_alert":inventory.low_stock_alert
    }
    return JSONResponse(content=content,
                            status_code=200)

@app.get("/inventory/update")
def analyze_revenue(
    inv_id: int = Query(None),
    current_stock: int=Query(None), 
    unit_price: int=Query(None), 
    cat_id: int= Query(None), 
):
    """
    Update inventory information.

    Parameters:
    - inv_id: ID of the inventory
    - current_stock: Updated current stock value
    - unit_price: Updated unit price value
    - cat_id: ID of the category

    Returns:
    - Updated inventory information
    """
    db = get_db()
    if (not inv_id and not cat_id and not current_stock and not unit_price):
        return JSONResponse(content="Atleast inv_id or cat_id is required.",
                            status_code=400)
    #Retrieve older and update with the new one
    inventory = db.query(Inventory).filter(Inventory.inv_id == inv_id).first()
    if inventory is not None:
        if current_stock:
            inventory.current_stock = current_stock
        elif unit_price:
            inventory.unit_price = unit_price
        
        #First update the Inventory changes table
        latest_changes = db.query(Inventory_Changes).filter(Inventory_Changes.inv_id == inv_id).order_by(Inventory_Changes.ch_date.desc()).first()
        if latest_changes is None:
            ch_id = random.randint(1000, 9999)

            changes = Inventory_Changes(
                inv_id = inv_id,
                ch_id = ch_id,
                ch_date=datetime.now(),
                current_stock = current_stock,
                unit_price = unit_price,
                name = inventory.name
                )
            db.add(changes)
        else:
            if current_stock:
                latest_changes.current_stock = current_stock
            elif unit_price:
                 latest_changes.unit_price = unit_price

        db.commit()
        content = {
            "current_stock": inventory.current_stock,
            "unit_price":inventory.unit_price,
            "updated_inventory_id" : inv_id
        }
        return JSONResponse(content=content,
                                status_code=200)
        

@app.get("/inventory/update/track")
def analyze_revenue(
    inv_id: int = Query(None)
):
    """
    Retrieve the inventory changes for a specific inventory.

    Parameters:
    - inv_id: ID of the inventory

    Returns:
    - List of inventory changes for the specified inventory
    """
    db = get_db()
    if (not inv_id):
        return JSONResponse(content="Atleast inv_id is required.",
                            status_code=400)
    inventory_changes = db.query(Inventory_Changes).filter(Inventory_Changes.inv_id == inv_id).all()
    if inventory_changes is not None:
        return inventory_changes
    else:
        return JSONResponse(content="No inventory change found for this inventory",
                                status_code=404)



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")