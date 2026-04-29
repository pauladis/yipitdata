"""
MCP Server for YipitData KPI Analytics
Exposes tools for LLMs to interact with KPI data
"""

import json
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import Server
from pydantic import AnyUrl
import logging
from app.database import SessionLocal, init_db
from app import services

logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Create MCP server
mcp = Server("yipitdata-kpi-server")


@mcp.tool()
def search_companies(
    query: str = None,
    sector: str = None
) -> str:
    """
    Search for companies by name/ticker or filter by sector.
    
    Args:
        query: Search term (company name or ticker)
        sector: Filter by sector name
    
    Returns:
        JSON list of companies with ticker, name, and sector
    """
    db = SessionLocal()
    try:
        results = services.get_companies(db, query=query, sector=sector)
        return json.dumps(results, default=str)
    finally:
        db.close()


@mcp.tool()
def get_company_kpis(ticker: str) -> str:
    """
    Get all available KPIs for a specific company.
    
    Args:
        ticker: Company ticker symbol (e.g., 'AAPL')
    
    Returns:
        JSON object with company info and list of KPIs
    """
    db = SessionLocal()
    try:
        result = services.get_company_kpis(db, ticker)
        if not result:
            return json.dumps({"error": f"Company {ticker} not found"})
        return result.model_dump_json()
    finally:
        db.close()


@mcp.tool()
def get_kpi_history(
    ticker: str,
    kpi_name: str,
    start_date: str = None,
    end_date: str = None,
    is_qtd: bool = False
) -> str:
    """
    Get historical or QTD (quarter-to-date) data for a KPI.
    
    Args:
        ticker: Company ticker symbol
        kpi_name: Name of the KPI (e.g., 'Total Revenue')
        start_date: Optional start date (YYYY-MM-DD format)
        end_date: Optional end date (YYYY-MM-DD format)
        is_qtd: If true, return QTD data; if false, return historical data
    
    Returns:
        JSON object with KPI history data including values and dates
    """
    from datetime import datetime
    
    db = SessionLocal()
    try:
        # Parse dates if provided
        start = None
        end = None
        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                return json.dumps({"error": "Invalid start_date format. Use YYYY-MM-DD"})
        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                return json.dumps({"error": "Invalid end_date format. Use YYYY-MM-DD"})
        
        result = services.get_kpi_history(
            db, ticker, kpi_name, 
            start_date=start, 
            end_date=end,
            is_qtd=is_qtd
        )
        if not result:
            return json.dumps({"error": f"No data found for {ticker} {kpi_name}"})
        return result.model_dump_json()
    finally:
        db.close()


@mcp.tool()
def get_kpi_summary(ticker: str, kpi_name: str) -> str:
    """
    Get comprehensive KPI summary with insights.
    
    This is the most important tool for understanding KPI performance.
    
    Args:
        ticker: Company ticker symbol
        kpi_name: Name of the KPI
    
    Returns:
        JSON object containing:
        - latest_quarter: Most recent quarterly estimate
        - previous_quarter: Previous quarter estimate (if available)
        - qoq_change_pct: Quarter-over-quarter percentage change
        - latest_qtd: Latest quarter-to-date estimate (if available)
        - qtd_vs_last_quarter_pct: QTD vs previous quarter percentage
        - trend: Direction indicator ('up', 'down', or 'flat')
    """
    db = SessionLocal()
    try:
        result = services.get_kpi_summary(db, ticker, kpi_name)
        if not result:
            return json.dumps({"error": f"KPI {kpi_name} not found for {ticker}"})
        return result.model_dump_json()
    finally:
        db.close()


@mcp.tool()
def compare_companies_kpi(tickers: str, kpi_name: str) -> str:
    """
    Compare a KPI across multiple companies.
    
    Args:
        tickers: Comma-separated list of ticker symbols (e.g., 'AAPL,GOOGL,META')
        kpi_name: Name of the KPI to compare
    
    Returns:
        JSON object with KPI comparison data for all companies
    """
    db = SessionLocal()
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(",")]
        result = services.compare_companies_kpi(db, ticker_list, kpi_name)
        if not result:
            return json.dumps({"error": f"Comparison data not found for {kpi_name}"})
        return result.model_dump_json()
    finally:
        db.close()


@mcp.tool()
def list_sectors() -> str:
    """
    Get a list of all available sectors in the database.
    
    Returns:
        JSON list of unique sectors
    """
    db = SessionLocal()
    try:
        from app.database import KPIData
        sectors = db.query(KPIData.sector).distinct().all()
        sector_list = [s[0] for s in sectors if s[0]]
        return json.dumps(sector_list)
    finally:
        db.close()


@mcp.tool()
def list_kpi_names() -> str:
    """
    Get a list of all available KPI names in the database.
    
    Returns:
        JSON list of unique KPI names
    """
    db = SessionLocal()
    try:
        from app.database import KPIData
        kpis = db.query(KPIData.kpi_name).distinct().all()
        kpi_list = [kpi[0] for kpi in kpis if kpi[0]]
        return json.dumps(kpi_list)
    finally:
        db.close()


async def main():
    """Run the MCP server"""
    async with mcp:
        logger.info("YipitData KPI MCP Server started")
        await mcp.wait_for_shutdown()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
