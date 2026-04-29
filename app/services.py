from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import KPIData
from app.schemas import KPISummary, QuarterData, CompanyKPIs, KPIInfo, KPIHistory, KPIDataResponse, KPIComparison, ComparisonPoint
from typing import List, Optional
from datetime import date


def get_companies(db: Session, query: str = None, sector: str = None) -> List[dict]:
    """Search companies by name/ticker or filter by sector"""
    q = db.query(KPIData.ticker, KPIData.company_name, KPIData.sector).distinct()
    
    if query:
        query_lower = f"%{query.lower()}%"
        q = q.filter(
            (KPIData.ticker.ilike(query_lower)) |
            (KPIData.company_name.ilike(query_lower))
        )
    
    if sector:
        q = q.filter(KPIData.sector.ilike(f"%{sector}%"))
    
    results = q.all()
    return [
        {"ticker": r[0], "company_name": r[1], "sector": r[2]}
        for r in results
    ]


def get_company_kpis(db: Session, ticker: str) -> Optional[CompanyKPIs]:
    """Get all KPIs for a company"""
    company = db.query(
        KPIData.ticker, 
        KPIData.company_name, 
        KPIData.sector
    ).filter(KPIData.ticker == ticker.upper()).distinct().first()
    
    if not company:
        return None
    
    kpis = db.query(KPIData.kpi_name, KPIData.unit).filter(
        KPIData.ticker == ticker.upper()
    ).distinct().all()
    
    return CompanyKPIs(
        ticker=company[0],
        company_name=company[1],
        sector=company[2],
        kpis=[KPIInfo(kpi_name=kpi[0], unit=kpi[1]) for kpi in kpis]
    )


def get_kpi_history(
    db: Session,
    ticker: str,
    kpi_name: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    is_qtd: bool = False
) -> Optional[KPIHistory]:
    """Get historical KPI data, optionally filtered by date range"""
    q = db.query(KPIData).filter(
        KPIData.ticker == ticker.upper(),
        KPIData.kpi_name == kpi_name,
        KPIData.is_qtd == is_qtd
    )
    
    if start_date:
        q = q.filter(KPIData.period_end >= start_date)
    if end_date:
        q = q.filter(KPIData.period_end <= end_date)
    
    q = q.order_by(KPIData.period_end)
    results = q.all()
    
    if not results:
        return None
    
    unit = results[0].unit
    return KPIHistory(
        kpi_name=kpi_name,
        unit=unit,
        ticker=ticker.upper(),
        data=[KPIDataResponse.from_orm(r) for r in results]
    )


def calculate_qoq_change(current: float, previous: float) -> Optional[float]:
    """Calculate quarter-over-quarter percentage change"""
    if previous == 0:
        return None
    return ((current - previous) / previous) * 100


def get_trend(qoq_change: Optional[float]) -> Optional[str]:
    """Determine trend direction"""
    if qoq_change is None:
        return None
    if qoq_change > 0.5:
        return "up"
    elif qoq_change < -0.5:
        return "down"
    else:
        return "flat"


def get_kpi_summary(db: Session, ticker: str, kpi_name: str) -> Optional[KPISummary]:
    """
    Get aggregated KPI insights:
    - Latest historical quarter
    - Previous quarter
    - QoQ change
    - Latest QTD
    - QTD vs last quarter comparison
    - Trend indicator
    """
    ticker = ticker.upper()
    
    # Get latest historical quarter
    latest_hist = db.query(KPIData).filter(
        KPIData.ticker == ticker,
        KPIData.kpi_name == kpi_name,
        KPIData.is_qtd == False
    ).order_by(desc(KPIData.period_end)).first()
    
    if not latest_hist:
        return None
    
    unit = latest_hist.unit
    latest_quarter = QuarterData(
        period_end=latest_hist.period_end,
        fiscal_quarter=latest_hist.fiscal_quarter,
        value=latest_hist.value
    )
    
    # Get previous quarter
    previous_quarter = None
    qoq_change_pct = None
    previous_hist = db.query(KPIData).filter(
        KPIData.ticker == ticker,
        KPIData.kpi_name == kpi_name,
        KPIData.is_qtd == False,
        KPIData.period_end < latest_hist.period_end
    ).order_by(desc(KPIData.period_end)).first()
    
    if previous_hist:
        previous_quarter = QuarterData(
            period_end=previous_hist.period_end,
            fiscal_quarter=previous_hist.fiscal_quarter,
            value=previous_hist.value
        )
        qoq_change_pct = calculate_qoq_change(latest_hist.value, previous_hist.value)
    
    # Get latest QTD (most recent as_of_date)
    latest_qtd = None
    qtd_vs_last_quarter_pct = None
    latest_qtd_record = db.query(KPIData).filter(
        KPIData.ticker == ticker,
        KPIData.kpi_name == kpi_name,
        KPIData.is_qtd == True
    ).order_by(desc(KPIData.as_of_date)).first()
    
    if latest_qtd_record:
        latest_qtd = QuarterData(
            period_end=latest_qtd_record.period_end,
            fiscal_quarter=latest_qtd_record.fiscal_quarter,
            value=latest_qtd_record.value
        )
        # Compare QTD vs previous quarter (or latest if no previous)
        compare_value = previous_hist.value if previous_hist else latest_hist.value
        qtd_vs_last_quarter_pct = calculate_qoq_change(latest_qtd_record.value, compare_value)
    
    # Determine trend
    trend = get_trend(qoq_change_pct)
    
    return KPISummary(
        kpi=kpi_name,
        unit=unit,
        latest_quarter=latest_quarter,
        previous_quarter=previous_quarter,
        qoq_change_pct=qoq_change_pct,
        latest_qtd=latest_qtd,
        qtd_vs_last_quarter_pct=qtd_vs_last_quarter_pct,
        trend=trend
    )


def compare_companies_kpi(
    db: Session,
    tickers: List[str],
    kpi_name: str
) -> Optional[KPIComparison]:
    """Compare a KPI across multiple companies"""
    tickers = [t.upper() for t in tickers]
    
    # Get unit from first available
    first_record = db.query(KPIData).filter(
        KPIData.ticker.in_(tickers),
        KPIData.kpi_name == kpi_name
    ).first()
    
    if not first_record:
        return None
    
    unit = first_record.unit
    
    # Get latest value for each company
    comparison_data = []
    for ticker in tickers:
        latest = db.query(KPIData).filter(
            KPIData.ticker == ticker,
            KPIData.kpi_name == kpi_name,
            KPIData.is_qtd == False
        ).order_by(desc(KPIData.period_end)).first()
        
        if latest:
            company_info = db.query(KPIData.company_name).filter(
                KPIData.ticker == ticker
            ).first()
            comparison_data.append(
                ComparisonPoint(
                    ticker=ticker,
                    company_name=company_info[0] if company_info else ticker,
                    latest_value=latest.value,
                    latest_date=latest.period_end
                )
            )
    
    return KPIComparison(
        kpi_name=kpi_name,
        unit=unit,
        data=comparison_data
    )
