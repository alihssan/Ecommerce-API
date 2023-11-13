# Project Name

Description of your project.

## Project Setup

### Requirements
- Python (version x.x)
- MySQL Server
- MySQL Workbench

### Installation

1. Clone the repository:

```bash
git clone https://github.com/alihssan/Ecommerce-API.git
cd Ecommerce-API
```

2. Activate virtual env

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use 'venv\Scripts\activate'
```

3. Install Dependencies
```bash
pip install -r requirements.txt
```

4. Setup MySQL Workbench

Open MySQL Workbench and connect to your MySQL Server.

Create a new schema/database for your project.

Set the database connection details in the .env file:

```bash
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/your_database_name

```

5. Running models.py

```bash
python models.py

```

6. Running Data Ingestion Script

```bash
python data_ingestion.py

```

7. Running the FastAPI Server
```bash
uvicorn main:app --reload

```


*

## *Endpoints

**

**Retrieve Sales Data**

**Endpoint**: /sales/filter

**Parameters:**

  sale_id: int (optional)

inventory_id: int (optional)

category_id: int (optional)

start_date: date (optional)

end_date: date (optional)

**Description**: Retrieve sales data based on specified parameters.

  

**

## Analyze Revenue

**

**Endpoint:** /sales/revenue

**Parameters:**

start_date: date (optional)

end_date: date (optional)

interval: str (default: "daily")

**Description:** Analyze revenue within a specified date range and interval.

  

## **Compare Revenue**

  

**Endpoint:** /sales/revenue/compare

**Parameters:**

category1: int (optional)

category2: int (optional)

start_date1: date (optional)

end_date1: date (optional)

start_date2: date (optional)

end_date2: date (optional)

**Description:** Compare revenue between two categories within specified date ranges.

  

## **Inventory Status**

**Endpoint:** /inventory/status

**Parameters:**

inv_id: int (optional)

cat_id: int (optional)

**Description:** Retrieve current stock and low stock alert status for an inventory item.

  

## **Update Inventory**

**Endpoint:** /inventory/update

**Parameters:**

inv_id: int (required)

current_stock: int (optional)

unit_price: int (optional)

cat_id: int (optional)

**Description:** Update inventory details and track changes.

  

## **Inventory Update History**

**Endpoint:** /inventory/update/track

**Parameters:**

  inv_id: int (required)

**Description:** Retrieve the update history of an inventory item.