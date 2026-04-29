from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


class KPIDataResponse(BaseModel):
    id: int
    ticker: str
    company_name: Optional[str] = None
    sector: Optional[str] = None
    kpi_name: str
    unit: Optional[str] = None
    period_start: Optional[date] = None
    period_end: date
    fiscal_quarter: Optional[str] = None
    value: float
    is_qtd: bool
    as_of_date: Optional[date] = None

    class Config:
        from_attributes = True


class CompanyInfo(BaseModel):
    ticker: str
    company_name: str
    sector: str


class KPIInfo(BaseModel):
    kpi_name: str
    unit: Optional[str] = None


class QuarterData(BaseModel):
    period_end: date
    fiscal_quarter: Optional[str] = None
    value: float


class KPISummary(BaseModel):
    kpi: str
    unit: Optional[str] = None
    latest_quarter: Optional[QuarterData] = None
    previous_quarter: Optional[QuarterData] = None
    qoq_change_pct: Optional[float] = None
    latest_qtd: Optional[QuarterData] = None
    qtd_vs_last_quarter_pct: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "flat"


class CompanyKPIs(BaseModel):
    ticker: str
    company_name: str
    sector: str
    kpis: List[KPIInfo]


class KPIHistory(BaseModel):
    kpi_name: str
    unit: Optional[str] = None
    ticker: str
    data: List[KPIDataResponse]


class ComparisonPoint(BaseModel):
    ticker: str
    company_name: str
    latest_value: float
    latest_date: date


class KPIComparison(BaseModel):
    kpi_name: str
    unit: Optional[str] = None
    data: List[ComparisonPoint]
