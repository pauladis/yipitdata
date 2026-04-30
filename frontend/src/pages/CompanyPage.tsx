import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { ArrowUp, ArrowDown, Minus, Loader } from 'lucide-react';
import apiClient, { CompanyKPIs, KPISummary, KPIHistory } from '../utils/api';
import '../styles/CompanyPage.css';

const CompanyPage: React.FC = () => {
  const { ticker } = useParams<{ ticker: string }>();
  const navigate = useNavigate();

  const [company, setCompany] = useState<CompanyKPIs | null>(null);
  const [selectedKPI, setSelectedKPI] = useState<string | null>(null);
  const [summary, setSummary] = useState<KPISummary | null>(null);
  const [history, setHistory] = useState<KPIHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartType, setChartType] = useState<'line' | 'bar'>('line');
  
  // Date range filters
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  useEffect(() => {
    if (ticker) {
      loadCompanyData();
    }
  }, [ticker]);

  useEffect(() => {
    if (ticker && selectedKPI) {
      loadKPIData();
    }
  }, [ticker, selectedKPI, startDate, endDate]);

  const loadCompanyData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.getCompanyKPIs(ticker!);
      setCompany(response.data);
      if (response.data.kpis.length > 0) {
        setSelectedKPI(response.data.kpis[0].kpi_name);
      }
    } catch (err) {
      setError('Failed to load company data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadKPIData = async () => {
    if (!selectedKPI) return;

    try {
      const [summaryRes, historyRes] = await Promise.all([
        apiClient.getKPISummary(ticker!, selectedKPI),
        apiClient.getKPIHistory(ticker!, selectedKPI, startDate || undefined, endDate || undefined),
      ]);
      setSummary(summaryRes.data);
      setHistory(historyRes.data);
    } catch (err) {
      console.error('Failed to load KPI data', err);
    }
  };

  const handleResetDates = () => {
    setStartDate('');
    setEndDate('');
  };

  if (loading) {
    return (
      <div className="company-page">
        <div className="loading">
          <Loader size={32} className="spinner" />
          <p>Loading company data...</p>
        </div>
      </div>
    );
  }

  if (error || !company) {
    return (
      <div className="company-page">
        <button onClick={() => navigate('/')} className="btn btn-secondary">
          Back to Search
        </button>
        <div className="error-message">{error || 'Company not found'}</div>
      </div>
    );
  }

  const chartData = history?.data.map((d) => ({
    date: d.period_end,
    value: d.value,
    quarter: d.fiscal_quarter,
  })) || [];

  const getTrendIcon = (trend?: string) => {
    if (trend === 'up') return <ArrowUp size={20} className="trend-up" />;
    if (trend === 'down') return <ArrowDown size={20} className="trend-down" />;
    return <Minus size={20} className="trend-flat" />;
  };

  return (
    <div className="company-page">
      <button onClick={() => navigate('/')} className="btn btn-secondary">
        ← Back to Search
      </button>

      <section className="company-header">
        <div>
          <h1>{company.ticker}</h1>
          <p className="company-name">{company.company_name}</p>
          <p className="company-sector">Sector: {company.sector}</p>
        </div>
      </section>

      <section className="kpi-selector">
        <h3>Select KPI</h3>
        <div className="kpi-buttons">
          {company.kpis.map((kpi) => (
            <button
              key={kpi.kpi_name}
              className={`kpi-btn ${selectedKPI === kpi.kpi_name ? 'active' : ''}`}
              onClick={() => setSelectedKPI(kpi.kpi_name)}
            >
              {kpi.kpi_name}
            </button>
          ))}
        </div>
      </section>

      {selectedKPI && summary && (
        <>
          <section className="summary-section">
            <h3>KPI Summary: {selectedKPI}</h3>
            <div className="summary-grid">
              {summary.latest_quarter && (
                <div className="summary-card">
                  <h4>Latest Quarter</h4>
                  <p className="quarter-label">{summary.latest_quarter.fiscal_quarter}</p>
                  <p className="value">
                    {summary.latest_quarter.value.toLocaleString('en-US', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </p>
                  <p className="unit">{summary.unit || ''}</p>
                </div>
              )}
              {summary.qoq_change_pct !== null && summary.qoq_change_pct !== undefined && (
                <div className="summary-card">
                  <h4>QoQ Change</h4>
                  <div className="change-value">
                    {getTrendIcon(summary.trend)}
                    <span>
                      {summary.qoq_change_pct > 0 ? '+' : ''}
                      {summary.qoq_change_pct.toFixed(2)}%
                    </span>
                  </div>
                </div>
              )}
              {summary.latest_qtd && (
                <div className="summary-card">
                  <h4>Latest QTD</h4>
                  <p className="quarter-label">Current Quarter</p>
                  <p className="value">
                    {summary.latest_qtd.value.toLocaleString('en-US', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </p>
                  {summary.qtd_vs_last_quarter_pct !== null && summary.qtd_vs_last_quarter_pct !== undefined && (
                    <p className="qtd-change">
                      {summary.qtd_vs_last_quarter_pct > 0 ? '+' : ''}
                      {summary.qtd_vs_last_quarter_pct.toFixed(2)}%
                    </p>
                  )}
                </div>
              )}
            </div>
          </section>

          {history && chartData.length > 0 && (
            <section className="chart-section">
              <div className="chart-header">
                <h3>Historical Data</h3>
                <div className="chart-controls">
                  <button
                    className={`chart-btn ${chartType === 'line' ? 'active' : ''}`}
                    onClick={() => setChartType('line')}
                  >
                    Line Chart
                  </button>
                  <button
                    className={`chart-btn ${chartType === 'bar' ? 'active' : ''}`}
                    onClick={() => setChartType('bar')}
                  >
                    Bar Chart
                  </button>
                </div>
              </div>

              <div className="date-filter">
                <div className="date-inputs">
                  <div className="date-group">
                    <label>Start Date:</label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="date-input"
                    />
                  </div>
                  <div className="date-group">
                    <label>End Date:</label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="date-input"
                    />
                  </div>
                  <button
                    onClick={handleResetDates}
                    className="btn btn-secondary"
                    style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                  >
                    Reset Dates
                  </button>
                </div>
              </div>

              <ResponsiveContainer width="100%" height={400}>
                {chartType === 'line' ? (
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="quarter"
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis />
                    <Tooltip
                      formatter={(value: number) =>
                        value.toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })
                      }
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#3b82f6"
                      dot={{ fill: '#3b82f6', r: 5 }}
                      activeDot={{ r: 7 }}
                    />
                  </LineChart>
                ) : (
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="quarter"
                      angle={-45}
                      textAnchor="end"
                      height={80}
                    />
                    <YAxis />
                    <Tooltip
                      formatter={(value: number) =>
                        value.toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })
                      }
                    />
                    <Bar dataKey="value" fill="#3b82f6" />
                  </BarChart>
                )}
              </ResponsiveContainer>
              <p className="chart-footer">
                Last updated: {new Date().toLocaleDateString()}
                {startDate || endDate ? ` | Filtered: ${startDate || 'Start'} to ${endDate || 'End'}` : ''}
              </p>
            </section>
          )}
        </>
      )}
    </div>
  );
};

export default CompanyPage;
