import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Loader } from 'lucide-react';
import apiClient, { Company } from '../utils/api';
import '../styles/HomePage.css';

const HomePage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sectorFilter, setSectorFilter] = useState('');
  const [companies, setCompanies] = useState<Company[]>([]);
  const [sectors, setSectors] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async (query?: string, sector?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.searchCompanies(query, sector);
      setCompanies(response.data.companies);
      
      // Extract unique sectors
      const uniqueSectors = Array.from(
        new Set(response.data.companies.map(c => c.sector))
      ).sort();
      setSectors(uniqueSectors);
    } catch (err) {
      setError('Failed to fetch companies');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCompanies(searchQuery || undefined, sectorFilter || undefined);
  };

  const handleCompanyClick = (ticker: string) => {
    navigate(`/company/${ticker}`);
  };

  const handleReset = () => {
    setSearchQuery('');
    setSectorFilter('');
    fetchCompanies();
  };

  return (
    <div className="home-page">
      <section className="search-section">
        <h2>Find Companies & KPIs</h2>
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-inputs">
            <div className="input-group">
              <input
                type="text"
                placeholder="Search by ticker or company name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
              <Search size={20} className="search-icon" />
            </div>
            <select
              value={sectorFilter}
              onChange={(e) => setSectorFilter(e.target.value)}
              className="sector-select"
            >
              <option value="">All Sectors</option>
              {sectors.map((sector) => (
                <option key={sector} value={sector}>
                  {sector}
                </option>
              ))}
            </select>
          </div>
          <div className="search-buttons">
            <button type="submit" className="btn btn-primary">
              Search
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="btn btn-secondary"
            >
              Reset
            </button>
          </div>
        </form>
      </section>

      {error && <div className="error-message">{error}</div>}

      <section className="companies-section">
        {loading ? (
          <div className="loading">
            <Loader size={32} className="spinner" />
            <p>Loading companies...</p>
          </div>
        ) : companies.length > 0 ? (
          <div className="companies-grid">
            {companies.map((company) => (
              <div
                key={company.ticker}
                className="company-card"
                onClick={() => handleCompanyClick(company.ticker)}
              >
                <h3>{company.ticker}</h3>
                <p className="company-name">{company.company_name}</p>
                <p className="company-sector">{company.sector}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-results">
            <p>No companies found. Try a different search.</p>
          </div>
        )}
      </section>

      <section className="info-section">
        <h3>About This Platform</h3>
        <p>
          Explore quarterly KPI estimates for public companies. View historical
          data and quarter-to-date (QTD) estimates to understand performance
          trends at a glance.
        </p>
      </section>
    </div>
  );
};

export default HomePage;
