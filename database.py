from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ProductTotalSales(Base):
    __tablename__ = 'product_total_sales'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    item_id = Column(String)
    total_sales = Column(Float)
    total_units_ordered = Column(Integer)

class ProductAdSales(Base):
    __tablename__ = 'product_ad_sales'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    item_id = Column(String)
    ad_sales = Column(Float)
    impressions = Column(Integer)
    ad_spend = Column(Float)
    clicks = Column(Integer)
    units_sold = Column(Integer)

class ProductEligibility(Base):
    __tablename__ = 'product_eligibility'
    id = Column(Integer, primary_key=True)
    eligibility_datetime_utc = Column(DateTime)
    item_id = Column(String)
    eligibility = Column(String)
    message = Column(String)

def init_db():
    engine = create_engine('sqlite:///ecommerce.db')
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()