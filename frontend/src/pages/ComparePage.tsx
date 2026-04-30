import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Loader, X } from 'lucide-react';
import apiClient, { Company } from '../utils/api';
import '../styles/ComparePage.css';

interface ComparisonData {
  ticker: string;
  company_name: string;
  latest_value: number;
  latest_date: string;
}

const ComparePage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedTickers, setSelectedTickers] = useState<string[]>([]);
  const [tickerInput, setTickerInput] = useState<string>('');
  const [availableCompanies, setAvailableCompanies] = useState<Company[]>([]);
  const [filteredCompanies, setFilteredCompanies] = useState<Company[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [availableKPIs, setAvailableKPIs] = useState<string[]>([]);
  const [selectedKPI, setSelectedKPI] = useState<string | null>(null);
  const [comparisonData, setComparisonData] = useState<ComparisonData[]>([]);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load companies and KPIs on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load all companies for filtering
        const companiesResponse = await apiClient.searchCompanies();
        setAvailableCompanies(companiesResponse.data.companies);

        // Fetch available KPIs
        const kpisResponse = await fetch('http://localhost:8000/kpi/names');
        if (kpisResponse.ok) {
          const data = await kpisResponse.json();
          setAvailableKPIs(data);
        }
      } catch (err) {
        console.error('Failed to load data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // Handle ticker input changes and filter companies
  const handleTickerInputChange = (value: string) => {
    setTickerInput(value);
    if (value.trim()) {
      const filtered = availableCompanies.filter(
        (company) =>
          !selectedTickers.includes(company.ticker) &&
          (company.ticker.toUpperCase().includes(value.toUpperCase()) ||
            company.company_name.toUpperCase().includes(value.toUpperCase()))
      );
      setFilteredCompanies(filtered);
      setShowDropdown(true);
    } else {
      setFilteredCompanies([]);
      setShowDropdown(false);
    }
  };

  // Handle company selection from dropdown
  const handleSelectCompany = (company: Company) => {
    if (!selectedTickers.includes(company.ticker)) {
      setSelectedTickers([...selectedTickers, company.ticker]);
    }
    setTickerInput('');
    setFilteredCompanies([]);
    setShowDropdown(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false);
      }
    };

    if (showDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showDropdown]);

  const handleRemoveTicker = (ticker: string) => {
    setSelectedTickers(selectedTickers.filter((t) => t !== ticker));
  };

  const handleCompare = async () => {
    if (selectedTickers.length < 2) {
      setError('Please select at least 2 companies to compare');
      return;
    }

    if (!selectedKPI) {
      setError('Please select a KPI');
      return;
    }

    setComparing(true);
    setError(null);
    try {
      const response = await apiClient.compareCompaniesKPI(
        selectedTickers,
        selectedKPI
      );
      setComparisonData(response.data.data || []);
      if (response.data.data.length === 0) {
        setError('No data found for the selected companies and KPI');
      }
    } catch (err) {
      setError('Failed to fetch comparison data');
      console.error(err);
    } finally {
      setComparing(false);
    }
  };

  const chartData = comparisonData.map((d) => ({
    ticker: d.ticker,
    company: d.company_name,
    value: d.latest_value,
    date: d.latest_date,
  }));

  if (loading) {
    return (
      <div className="compare-page">
        <div className="loading">
          <Loader size={32} className="spinner" />
          <p>Loading data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="compare-page">
      <button onClick={() => navigate('/')} className="btn btn-secondary">
        ← Back to Search
      </button>

      <section className="compare-header">
        <h1>Compare KPI Across Companies</h1>
        <p>Select multiple companies and a KPI to compare their latest values</p>
      </section>

      <section className="compare-form">
        <div className="form-group">
          <label>Company Search:</label>
          <div className="company-search-container" ref={dropdownRef}>
            <div className="company-input-group">
              <input
                type="text"
                placeholder="Search by ticker or company name (e.g., AC, ACME)..."
                value={tickerInput}
                onChange={(e) => handleTickerInputChange(e.target.value)}
                onFocus={() => {
                  if (tickerInput.trim()) {
                    setShowDropdown(true);
                  }
                }}
                className="text-input"
              />
            </div>

            {showDropdown && filteredCompanies.length > 0 && (
              <div className="dropdown-list">
                {filteredCompanies.map((company) => (
                  <div
                    key={company.ticker}
                    className="dropdown-item"
                    onClick={() => handleSelectCompany(company)}
                  >
                    <div className="dropdown-ticker">{company.ticker}</div>
                    <div className="dropdown-details">
                      <div className="dropdown-name">{company.company_name}</div>
                      <div className="dropdown-sector">{company.sector}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {showDropdown && filteredCompanies.length === 0 && tickerInput.trim() && (
              <div className="dropdown-empty">
                <p>No companies found matching "{tickerInput}"</p>
              </div>
            )}
          </div>
        </div>

        {selectedTickers.length > 0 && (
          <div className="selected-tickers">
            <h4>Selected Companies ({selectedTickers.length}):</h4>
            <div className="ticker-tags">
              {selectedTickers.map((ticker) => {
                const company = availableCompanies.find((c) => c.ticker === ticker);
                return (
                  <div key={ticker} className="ticker-tag">
                    <div className="ticker-tag-info">
                      <span className="ticker-bold">{ticker}</span>
                      <span className="ticker-name">
                        {company?.company_name}
                      </span>
                    </div>
                    <button
                      onClick={() => handleRemoveTicker(ticker)}
                      className="remove-btn"
                    >
                      <X size={16} />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className="form-group">
          <label>Select KPI:</label>
          {availableKPIs.length > 0 ? (
            <div className="kpi-buttons">
              {availableKPIs.map((kpi) => (
                <button
                  key={kpi}
                  className={`kpi-btn ${selectedKPI === kpi ? 'active' : ''}`}
                  onClick={() => setSelectedKPI(kpi)}
                >
                  {kpi}
                </button>
              ))}
            </div>
          ) : (
            <p className="no-kpis">No KPIs available</p>
          )}
        </div>

        <button
          onClick={handleCompare}
          disabled={selectedTickers.length < 2 || !selectedKPI || comparing}
          className="btn btn-primary btn-large"
        >
          {comparing ? 'Comparing...' : 'Compare'}
        </button>
      </section>

      {error && <div className="error-message">{error}</div>}

      {!comparing && comparisonData.length > 0 && (
        <section className="comparison-results">
          <h2>Comparison Results: {selectedKPI}</h2>
          <p className="results-info">
            Showing latest values for {selectedTickers.length} companies
          </p>

          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="ticker" />
              <YAxis />
              <Tooltip
                formatter={(value: any) =>
                  typeof value === 'number'
                    ? value.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })
                    : value
                }
                labelFormatter={(label) => `Ticker: ${label}`}
              />
              <Legend />
              <Bar dataKey="value" fill="#3b82f6" name="Latest Value" />
            </BarChart>
          </ResponsiveContainer>

          <div className="comparison-table">
            <table>
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th>Company Name</th>
                  <th>Latest Value</th>
                  <th>As of Date</th>
                </tr>
              </thead>
              <tbody>
                {comparisonData.map((data) => (
                  <tr key={data.ticker}>
                    <td className="ticker-cell">
                      <strong>{data.ticker}</strong>
                    </td>
                    <td>{data.company_name}</td>
                    <td className="value-cell">
                      {data.latest_value.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </td>
                    <td>{new Date(data.latest_date).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
};

export default ComparePage;
