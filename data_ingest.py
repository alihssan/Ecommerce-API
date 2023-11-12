#create a script to put all the sales daat to db
import mysql.connector
from datetime import datetime
import json
import pandas as pd

def connect_to_mysql() -> mysql.connector:

    cnx = mysql.connector.connect(
        user="username",
        password="password",
        host="hostname",
        database="databasename",
        connection_timeout=10000
    )

    return cnx

cnx = connect_to_mysql()

def insert_cat_data(connection: cnx, 
                    cat_name: str, 
                    cat_id: int):

    cursor = connection.cursor()
    query = "INSERT INTO Categories (cat_id, cat_name) VALUES (%s, %s)"
    cursor.execute(query, (cat_id, cat_name))
    connection.commit()
    cursor.close()

def insert_inv_data(connection: cnx, 
                    inv_id: int, 
                    cat_id: int, 
                    current_stock: int, 
                    unit_price:int,
                    low_stock_alert: str ):

    cursor = connection.cursor()
    query = "INSERT INTO Inventory (inv_id, cat_id,current_stock,unit_price,low_stock_alert) VALUES (%s, %s,%s,%s,%s)"
    cursor.execute(query,(inv_id, cat_id,current_stock,unit_price,low_stock_alert))
    connection.commit()
    cursor.close()


def insert_sales_data(connection: cnx, 
                    inv_id: int, 
                    sale_id: int, 
                    timestamp: datetime , 
                    quantity_sold:int,
                    price_per_quantity: int):
    
    cursor = connection.cursor()
    query = "INSERT INTO Sales (sale_id, inv_id,timestamp,quantity_sold,price_per_quantity) VALUES (%s, %s,%s,%s,%s)"
    cursor.execute(query,(inv_id, sale_id,timestamp,quantity_sold,price_per_quantity))
    connection.commit()
    cursor.close()


data = pd.read_json("data.json")
print(data)
