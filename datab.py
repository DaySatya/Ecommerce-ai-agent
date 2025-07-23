# datab.py

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import pandas as pd
import os

Base = declarative_base()

# Define your SQLAlchemy models FIRST
class ProductTotalSales(Base):
    __tablename__ = 'product_total_sales'
    date = Column(DateTime, primary_key=True)
    item_id = Column(String, primary_key=True)
    total_sales = Column(Float)
    total_units_ordered = Column(Integer)

class ProductAdSales(Base):
    __tablename__ = 'product_ad_sales'
    date = Column(DateTime, primary_key=True)
    item_id = Column(String, primary_key=True)
    ad_sales = Column(Float)
    impressions = Column(Integer)
    ad_spend = Column(Float)
    clicks = Column(Integer)
    units_sold = Column(Integer)

class ProductEligibility(Base):
    __tablename__ = 'product_eligibility'
    eligibility_datetime_utc = Column(DateTime, primary_key=True)
    item_id = Column(String, primary_key=True)
    eligibility = Column(String)
    message = Column(String)

# Define the MODEL_MAPPING after the class definitions
MODEL_MAPPING = {
    'product_total_sales': ProductTotalSales,
    'product_ad_sales': ProductAdSales,
    'product_eligibility': ProductEligibility,
}

def init_db():
    engine = create_engine('sqlite:///./ecommerce.db')
    Base.metadata.create_all(engine)

    print("\n--- Attempting to load CSV data ---")
    load_data_from_csv(engine, 'product_total_sales', 'product_total_sales.csv')
    load_data_from_csv(engine, 'product_ad_sales', 'product_ad_sales.csv')
    load_data_from_csv(engine, 'product_eligibility', 'product_eligibility.csv')
    print("--- CSV data load attempts complete ---\n")

    return engine

def load_data_from_csv(engine, table_name, csv_file_name):
    """Loads data from a CSV file into the specified database table."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_full_path = os.path.join(current_dir, 'data', csv_file_name)

    print(f"Checking for CSV: {csv_full_path}")
    if not os.path.exists(csv_full_path):
        print(f"ERROR: CSV file NOT FOUND at {csv_full_path}. Skipping data load for {table_name}.")
        return

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get the ModelClass from the MODEL_MAPPING dictionary
        ModelClass = MODEL_MAPPING.get(table_name)

        if ModelClass is None:
            # This should ideally not happen if MODEL_MAPPING is correctly defined
            print(f"ERROR: Model class for table '{table_name}' not found in MODEL_MAPPING. Cannot check existing data.")
            session.close() # Close session even on error
            return

        if session.query(ModelClass).count() > 0:
            print(f"Table '{table_name}' already contains data. Skipping CSV load to prevent duplicates.")
            session.close()
            return

        print(f"Loading data from '{csv_file_name}' into '{table_name}'...")
        df = pd.read_csv(csv_full_path)

        # Your extensive print statements for debugging CSV content and dtypes:
        print(f"Initial DataFrame for '{table_name}' (first 5 rows):\n{df.head().to_string()}")
        print(f"Initial dtypes for '{table_name}':\n{df.dtypes}")

        # --- Date/Datetime Conversion ---
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            if df['date'].isna().any():
                print(f"Warning: Some 'date' values in '{table_name}' could not be parsed and were coerced to NaT. Dropping these rows.")
            df.dropna(subset=['date'], inplace=True)

        if 'eligibility_datetime_utc' in df.columns:
            df['eligibility_datetime_utc'] = pd.to_datetime(df['eligibility_datetime_utc'], errors='coerce')
            if df['eligibility_datetime_utc'].isna().any():
                print(f"Warning: Some 'eligibility_datetime_utc' values in '{table_name}' could not be parsed and were coerced to NaT. Dropping these rows.")
            df.dropna(subset=['eligibility_datetime_utc'], inplace=True)

        # --- Numeric Column Conversion ---
        numeric_cols = {
            'product_total_sales': ['total_sales', 'total_units_ordered'],
            'product_ad_sales': ['ad_sales', 'impressions', 'ad_spend', 'clicks', 'units_sold']
        }

        if table_name in numeric_cols:
            for col in numeric_cols[table_name]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    if df[col].isna().any():
                        print(f"Warning: Some '{col}' values in '{table_name}' could not be converted to numeric and were coerced to NaN. Dropping these rows.")
                    df.dropna(subset=[col], inplace=True)
                else:
                    print(f"Warning: Expected numeric column '{col}' not found in '{table_name}' CSV.")

        print(f"DataFrame for '{table_name}' after conversions and NaN drops (first 5 rows):\n{df.head().to_string()}")
        print(f"Dtypes after conversions for '{table_name}':\n{df.dtypes}")
        print(f"Number of rows remaining for '{table_name}' after cleaning: {len(df)}")

        if not df.empty:
            df.to_sql(table_name, con=engine, if_exists='append', index=False)
            session.commit()
            print(f"Successfully loaded data into '{table_name}'. Rows inserted: {len(df)}")
        else:
            print(f"No valid data to load for '{table_name}' after processing CSV (DataFrame is empty).")

    except Exception as e:
        session.rollback()
        print(f"CRITICAL ERROR loading data for '{table_name}' from '{csv_file_name}': {e}")
    finally:
        session.close()

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == '__main__':
    print("Initializing database and attempting to load CSV data...")
    init_db()
    print("Database initialization complete. Verifying data counts:")

    engine = create_engine('sqlite:///./ecommerce.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        print("\nVerifying data in product_total_sales:")
        result = session.execute(text("SELECT COUNT(*) FROM product_total_sales;"))
        count = result.scalar_one()
        print(f"product_total_sales has {count} rows.")

        print("\nVerifying data in product_ad_sales:")
        result = session.execute(text("SELECT COUNT(*) FROM product_ad_sales;"))
        count = result.scalar_one()
        print(f"product_ad_sales has {count} rows.")

        print("\nVerifying data in product_eligibility:")
        result = session.execute(text("SELECT COUNT(*) FROM product_eligibility;"))
        count = result.scalar_one()
        print(f"product_eligibility has {count} rows.")

    finally:
        session.close()