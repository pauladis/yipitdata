import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Loader } from 'lucide-react';
import apiClient, { Company } from '../utils/api';
import '../styles/HomePage.css';

const HomePage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sectorFilter, setSectorFilter] = useState('');
  const [companies, setCompanies] = useState<Company[]>([]);
  const [allCompanies, setAllCompanies] = useState<Company[]>([]);
  const [filteredCompanies, setFilteredCompanies] = useState<Company[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [sectors, setSectors] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchCompanies();
  }, []);

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

  const fetchCompanies = async (query?: string, sector?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.searchCompanies(query, sector);
      setCompanies(response.data.companies);
      setAllCompanies(response.data.companies);
      
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

  const handleSearchInputChange = (value: string) => {
    setSearchQuery(value);
    if (value.trim()) {
      const filtered = allCompanies.filter(
        (company) =>
          company.ticker.toUpperCase().includes(value.toUpperCase()) ||
          company.company_name.toUpperCase().includes(value.toUpperCase())
      );
      setFilteredCompanies(filtered);
      setShowDropdown(true);
    } else {
      setFilteredCompanies([]);
      setShowDropdown(false);
    }
  };

  const handleSelectCompany = (ticker: string) => {
    navigate(`/company/${ticker}`);
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
            <div className="input-group search-dropdown-container" ref={dropdownRef}>
              <input
                type="text"
                placeholder="Search by ticker or company name (e.g., AC, ACME)..."
                value={searchQuery}
                onChange={(e) => handleSearchInputChange(e.target.value)}
                onFocus={() => {
                  if (searchQuery.trim()) {
                    setShowDropdown(true);
                  }
                }}
                className="search-input"
              />
              <Search size={20} className="search-icon" />
              
              {showDropdown && filteredCompanies.length > 0 && (
                <div className="search-dropdown-list">
                  {filteredCompanies.map((company) => (
                    <div
                      key={company.ticker}
                      className="search-dropdown-item"
                      onClick={() => handleSelectCompany(company.ticker)}
                    >
                      <div className="search-dropdown-ticker">{company.ticker}</div>
                      <div className="search-dropdown-details">
                        <div className="search-dropdown-name">{company.company_name}</div>
                        <div className="search-dropdown-sector">{company.sector}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {showDropdown && filteredCompanies.length === 0 && searchQuery.trim() && (
                <div className="search-dropdown-empty">
                  <p>No companies found matching "{searchQuery}"</p>
                </div>
              )}
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
