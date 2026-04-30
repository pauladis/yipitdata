import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Search } from 'lucide-react';
import apiClient from './utils/api';
import HomePage from './pages/HomePage';
import CompanyPage from './pages/CompanyPage';
import ComparePage from './pages/ComparePage';
import './styles/App.css';

const App: React.FC = () => {
  const [isApiHealthy, setIsApiHealthy] = useState<boolean>(false);

  useEffect(() => {
    // Check API health on mount
    apiClient
      .health()
      .then(() => setIsApiHealthy(true))
      .catch(() => setIsApiHealthy(false));
  }, []);

  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <div className="header-container">
            <Link to="/" className="logo">
              <h1>📊 YipitData KPI Analytics</h1>
            </Link>
            <nav className="nav-links">
              <Link to="/" className="nav-link">Home</Link>
              <Link to="/compare" className="nav-link">Compare</Link>
            </nav>
            <div className="header-status">
              {isApiHealthy ? (
                <span className="status-healthy">● API Connected</span>
              ) : (
                <span className="status-error">● API Error</span>
              )}
            </div>
          </div>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/company/:ticker" element={<CompanyPage />} />
            <Route path="/compare" element={<ComparePage />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>&copy; 2024 YipitData KPI Analytics. All rights reserved.</p>
        </footer>
      </div>
    </Router>
  );
};

export default App;
