from sqlalchemy import Column, Integer, String,Text, create_engine,DateTime,Double,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
import os
from sqlalchemy.sql import func
from dotenv import load_dotenv


load_dotenv()
database_url = os.getenv("DATABASE_URL")
Base = declarative_base()


class Inventory(Base):
    __tablename__ = "Inventory"

    inv_id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, index=True)
    current_stock = Column(Integer)
    unit_price = Column(Integer)
    cat_id = Column(Integer,ForeignKey('Categories.cat_id'))
    low_stock_alert = Column(String(20))
    inv_id_ch_fk = relationship('Inventory_Changes', back_populates='inventory')
    inv_id_sales_fk = relationship('Sales', back_populates='inventory')
    category = relationship('Categories', back_populates='cat_id_fk')

class Categories(Base):
    __tablename__ = "Categories"

    cat_id = Column(Integer, primary_key=True, index=True)
    cat_name = Column(String(45))
    cat_id_fk = relationship('Inventory', back_populates='category')

class Inventory_Changes(Base):
    __tablename__ = "Inventory_Changes"

    ch_id = Column(Integer, primary_key=True, index=True)
    inv_id = Column(Integer, ForeignKey('Inventory.inv_id'))
    ch_date = Column(DateTime, default=func.now())
    ch_field = Column(String(50))
    ch_field_qty = Column(Text)
    inventory = relationship('Inventory', back_populates='inv_id_ch_fk')

class Sales(Base):
    __tablename__ = "Sales"

    sale_id = Column(Double, primary_key=True, index=True)
    inv_id = Column(Integer, ForeignKey('Inventory.inv_id'))
    timestamp = Column(DateTime, default=func.now())
    quantity_sold = Column(Integer)
    price_per_quantity = Column(Integer)
    inventory = relationship('Inventory', back_populates='inv_id_sales_fk')

engine = create_engine(database_url)
Base.metadata.create_all(bind=engine)
