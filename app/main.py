from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db, init_db
from app.loader import load_csv_to_db
from app import services
from app.schemas import (
    KPISummary, CompanyKPIs, KPIHistory, 
    KPIComparison, KPIDataResponse
)
from typing import List, Optional
from datetime import date
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YipitData KPI API",
    description="KPI analytics API for public investor data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and load CSV on startup"""
    logger.info("Initializing database...")
    init_db()
    
    # Load CSV if it exists
    csv_path = os.getenv("CSV_PATH", "/app/data/kpi_sample_2000.csv")
    if os.path.exists(csv_path):
        try:
            load_csv_to_db(csv_path)
            logger.info("CSV data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
    else:
        logger.warning(f"CSV file not found at {csv_path}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============== Company Endpoints ==============

@app.get("/companies")
async def search_companies(
    query: Optional[str] = Query(None, description="Search by ticker or company name"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    db: Session = Depends(get_db)
):
    """Search for companies by name/ticker or filter by sector"""
    results = services.get_companies(db, query=query, sector=sector)
    return {"companies": results}


@app.get("/companies/{ticker}/kpis")
async def get_company_kpis(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get all available KPIs for a company"""
    result = services.get_company_kpis(db, ticker)
    if not result:
        raise HTTPException(status_code=404, detail="Company not found")
    return result


# ============== KPI Data Endpoints ==============

@app.get("/kpi/history")
async def get_kpi_history(
    ticker: str = Query(..., description="Company ticker"),
    kpi_name: str = Query(..., description="KPI name"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    is_qtd: bool = Query(False, description="Get QTD data instead of historical"),
    db: Session = Depends(get_db)
):
    """Get historical or QTD data for a KPI"""
    result = services.get_kpi_history(
        db, ticker, kpi_name, 
        start_date=start_date, 
        end_date=end_date,
        is_qtd=is_qtd
    )
    if not result:
        raise HTTPException(status_code=404, detail="KPI data not found")
    return result


@app.get("/kpi/qtd")
async def get_kpi_qtd(
    ticker: str = Query(..., description="Company ticker"),
    kpi_name: str = Query(..., description="KPI name"),
    db: Session = Depends(get_db)
):
    """Get latest QTD (quarter-to-date) data for a KPI"""
    result = services.get_kpi_history(db, ticker, kpi_name, is_qtd=True)
    if not result:
        raise HTTPException(status_code=404, detail="QTD data not found")
    return result


@app.get("/kpi/summary")
async def get_kpi_summary(
    ticker: str = Query(..., description="Company ticker"),
    kpi_name: str = Query(..., description="KPI name"),
    db: Session = Depends(get_db)
) -> KPISummary:
    """
    Get comprehensive KPI summary including:
    - Latest historical quarter
    - Previous quarter
    - QoQ change percentage
    - Latest QTD
    - QTD vs last quarter comparison
    - Trend indicator (up/down/flat)
    """
    result = services.get_kpi_summary(db, ticker, kpi_name)
    if not result:
        raise HTTPException(status_code=404, detail="KPI not found")
    return result


@app.get("/kpi/compare")
async def compare_companies_kpi(
    tickers: str = Query(..., description="Comma-separated list of tickers"),
    kpi_name: str = Query(..., description="KPI name"),
    db: Session = Depends(get_db)
) -> KPIComparison:
    """Compare a KPI across multiple companies"""
    ticker_list = [t.strip() for t in tickers.split(",")]
    result = services.compare_companies_kpi(db, ticker_list, kpi_name)
    if not result:
        raise HTTPException(status_code=404, detail="Comparison data not found")
    return result


# ============== Admin Endpoints ==============

@app.post("/admin/reload-data")
async def reload_data(
    csv_path: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Reload KPI data from CSV (admin endpoint)"""
    try:
        path = csv_path or os.getenv("CSV_PATH", "/app/data/kpi_sample_2000.csv")
        if not os.path.exists(path):
            raise HTTPException(status_code=400, detail=f"CSV file not found at {path}")
        
        load_csv_to_db(path)
        return {"message": "Data reloaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
