from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kpi.db")

# Configure connection args based on database type
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
elif "postgresql" in DATABASE_URL:
    connect_args = {"connect_timeout": 10}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class KPIData(Base):
    __tablename__ = "kpi_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Company info
    ticker = Column(String, nullable=False, index=True)
    company_name = Column(String)
    sector = Column(String)
    
    # KPI info
    kpi_name = Column(String, nullable=False, index=True)
    unit = Column(String)
    
    # Temporal data
    period_start = Column(Date)
    period_end = Column(Date, nullable=False, index=True)
    fiscal_quarter = Column(String)
    
    # Value and metadata
    value = Column(Float, nullable=False)
    is_qtd = Column(Boolean, default=False, index=True)
    as_of_date = Column(Date)
    
    # Timestamps
    created_at = Column(Date, default=datetime.utcnow)


# Composite indexes for common queries
Index("idx_lookup", KPIData.ticker, KPIData.kpi_name)
Index("idx_time", KPIData.ticker, KPIData.kpi_name, KPIData.period_end)
Index("idx_qtd", KPIData.ticker, KPIData.kpi_name, KPIData.is_qtd, KPIData.as_of_date)
Index("idx_company_kpis", KPIData.ticker, KPIData.kpi_name, KPIData.period_end.desc())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
