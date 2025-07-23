import pandas as pd
from sqlalchemy import create_engine
from database import ProductTotalSales, ProductAdSales, ProductEligibility

def load_data():
    engine = create_engine('sqlite:///ecommerce.db')
    
    # Load and transform data (replace with your actual file paths)
    total_sales_df = pd.read_csv('product_total_sales.csv')
    ad_sales_df = pd.read_csv('product_ad_sales.csv')
    eligibility_df = pd.read_csv('product_eligibility.csv')
    
    # Convert date columns
    total_sales_df['date'] = pd.to_datetime(total_sales_df['date'])
    ad_sales_df['date'] = pd.to_datetime(ad_sales_df['date'])
    eligibility_df['eligibility_datetime_utc'] = pd.to_datetime(eligibility_df['eligibility_datetime_utc'])
    
    # Load data to SQL
    total_sales_df.to_sql('product_total_sales', engine, if_exists='replace', index=False)
    ad_sales_df.to_sql('product_ad_sales', engine, if_exists='replace', index=False)
    eligibility_df.to_sql('product_eligibility', engine, if_exists='replace', index=False)

if __name__ == '__main__':
    load_data()