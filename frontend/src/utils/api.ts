import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Company {
  ticker: string;
  company_name: string;
  sector: string;
}

export interface KPIInfo {
  kpi_name: string;
  unit?: string;
}

export interface CompanyKPIs {
  ticker: string;
  company_name: string;
  sector: string;
  kpis: KPIInfo[];
}

export interface QuarterData {
  period_end: string;
  fiscal_quarter?: string;
  value: number;
}

export interface KPISummary {
  kpi: string;
  unit?: string;
  latest_quarter?: QuarterData;
  previous_quarter?: QuarterData;
  qoq_change_pct?: number;
  latest_qtd?: QuarterData;
  qtd_vs_last_quarter_pct?: number;
  trend?: 'up' | 'down' | 'flat';
}

export interface KPIDataPoint {
  id: number;
  ticker: string;
  company_name?: string;
  sector?: string;
  kpi_name: string;
  unit?: string;
  period_start?: string;
  period_end: string;
  fiscal_quarter?: string;
  value: number;
  is_qtd: boolean;
  as_of_date?: string;
}

export interface KPIHistory {
  kpi_name: string;
  unit?: string;
  ticker: string;
  data: KPIDataPoint[];
}

export const apiClient = {
  // Companies
  searchCompanies: (query?: string, sector?: string) =>
    api.get<{ companies: Company[] }>('/companies', {
      params: { query, sector },
    }),

  getCompanyKPIs: (ticker: string) =>
    api.get<CompanyKPIs>(`/companies/${ticker}/kpis`),

  // KPI Data
  getKPIHistory: (
    ticker: string,
    kpiName: string,
    startDate?: string,
    endDate?: string,
    isQtd: boolean = false
  ) =>
    api.get<KPIHistory>('/kpi/history', {
      params: {
        ticker,
        kpi_name: kpiName,
        start_date: startDate,
        end_date: endDate,
        is_qtd: isQtd,
      },
    }),

  getKPISummary: (ticker: string, kpiName: string) =>
    api.get<KPISummary>('/kpi/summary', {
      params: {
        ticker,
        kpi_name: kpiName,
      },
    }),

  getKPIQTD: (ticker: string, kpiName: string) =>
    api.get<KPIHistory>('/kpi/qtd', {
      params: {
        ticker,
        kpi_name: kpiName,
      },
    }),

  compareCompaniesKPI: (tickers: string[], kpiName: string) =>
    api.get('/kpi/compare', {
      params: {
        tickers: tickers.join(','),
        kpi_name: kpiName,
      },
    }),

  // Health
  health: () => api.get('/health'),
};

export default apiClient;
