import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import KPIData, engine, SessionLocal, init_db
import logging

logger = logging.getLogger(__name__)


def load_csv_to_db(csv_path: str) -> None:
    """
    Load KPI data from CSV file into SQLite database.
    Replaces existing data (idempotent).
    """
    logger.info(f"Loading CSV from {csv_path}")
    
    # Initialize database
    init_db()
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    # Clean up column names
    df.columns = df.columns.str.lower().str.strip()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(KPIData).delete()
        db.commit()
        logger.info("Cleared existing KPI data")
        
        # Process and insert data
        records = []
        for idx, row in df.iterrows():
            # Parse dates
            period_end = pd.to_datetime(row.get('period_end')).date() if pd.notna(row.get('period_end')) else None
            period_start = pd.to_datetime(row.get('period_start')).date() if pd.notna(row.get('period_start')) else None
            as_of = pd.to_datetime(row.get('as_of')).date() if pd.notna(row.get('as_of')) else None
            
            # Determine if QTD
            is_qtd = str(row.get('estimate_type', '')).lower() == 'qtd'
            
            kpi_record = KPIData(
                ticker=row.get('ticker', '').upper(),
                company_name=row.get('company_name', ''),
                sector=row.get('sector', ''),
                kpi_name=row.get('kpi', ''),
                unit=row.get('unit', ''),
                period_start=period_start,
                period_end=period_end,
                fiscal_quarter=row.get('period', ''),
                value=float(row.get('value', 0)),
                is_qtd=is_qtd,
                as_of_date=as_of,
                created_at=datetime.utcnow().date()
            )
            records.append(kpi_record)
        
        # Bulk insert
        db.bulk_save_objects(records, return_defaults=False)
        db.commit()
        logger.info(f"Successfully loaded {len(records)} records into database")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error loading CSV: {e}")
        raise
    finally:
        db.close()
