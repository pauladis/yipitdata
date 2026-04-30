# YipitData KPI Analytics Platform

A full-stack KPI analytics platform for exploring quarterly KPI estimates for public companies. Built with React, FastAPI, PostgreSQL, and integrated with Model Context Protocol (MCP) for AI agent access.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Key Features](#key-features)
- [Quick Start with Docker](#quick-start-with-docker)
- [API Endpoints](#api-endpoints)
- [MCP Server Integration](#mcp-server-integration)
- [Design Decisions & Trade-offs](#design-decisions--trade-offs)
- [Observability](#observability)

---

## 🏗️ Architecture

### System Overview

The platform is built as a three-tier application:

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3000)               │
│                                                             │
│  - HomePage: Company search with autocomplete              │
│  - CompanyPage: KPI detail view with charts               │
│  - ComparePage: Cross-company KPI comparison              │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                   │
│                                                             │
│  - REST API with 8 endpoints                              │
│  - MCP Server (7 tools for AI agents)                     │
│  - CSV data loader                                        │
│  - Business logic & data aggregation                      │
└────────────────────┬────────────────────────────────────────┘
                     │ SQLAlchemy ORM
┌────────────────────▼────────────────────────────────────────┐
│           PostgreSQL Database (Port 5432)                   │
│                                                             │
│  - kpi_data table (2000+ records)                         │
│  - Optimized indexes for performance                      │
│  - Historical + QTD quarterly data                        │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

**Table: kpi_data**

```
- ticker: VARCHAR (Company ticker symbol)
- company_name: VARCHAR (Full company name)
- sector: VARCHAR (Industry sector)
- kpi_name: VARCHAR (Key Performance Indicator name)
- unit: VARCHAR (Measurement unit: $MM, subs, %)
- period_end: DATE (End date of fiscal period)
- fiscal_quarter: VARCHAR (Q1, Q2, Q3, Q4)
- value: FLOAT (KPI value for the period)
- is_qtd: BOOLEAN (False=historical, True=quarter-to-date)
- as_of_date: DATE (When QTD estimate was generated)
```

**Indexes:**
- `(ticker, kpi_name)` - Fast KPI lookup per company
- `(ticker, kpi_name, period_end)` - Historical data retrieval
- `(ticker, kpi_name, is_qtd)` - QTD filtering

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, TypeScript, Recharts | Interactive UI with data visualization |
| **Backend** | FastAPI, Uvicorn, SQLAlchemy | RESTful API, async request handling, ORM |
| **Database** | PostgreSQL 15 | Reliable data storage with ACID guarantees |
| **DevOps** | Docker, Docker Compose | Containerization & orchestration |
| **Integration** | MCP (Model Context Protocol) | LLM/AI agent integration |
| **Styling** | Tailwind CSS, Lucide Icons | Modern responsive design |
| **Charts** | Recharts | Interactive data visualization |

---

## ✨ Key Features

### 1. Company Discovery
- **Smart Search**: Autocomplete company search by ticker or name
- **Sector Filtering**: Filter companies by industry sector
- **Real-time Results**: Instant filtering as you type

### 2. KPI Analysis
- **Historical Data**: View quarterly KPI trends over time
- **QTD Estimates**: Quarter-to-date performance tracking
- **Dual-axis Visualization**: Compare multiple metrics simultaneously
- **Chart Toggle**: Switch between line and bar charts
- **Date Range Filtering**: Analyze specific time periods

### 3. Performance Metrics
- **Latest Quarter Value**: Most recent quarterly estimate
- **QoQ Change**: Quarter-over-quarter percentage changes
- **Trend Indicators**: Visual up/down/flat trend signals
- **QTD Comparison**: QTD vs previous quarter analysis

### 4. Cross-Company Comparison
- **Multi-company KPI Compare**: Compare any KPI across multiple companies
- **Sortable Results**: Bar chart and table views
- **Latest Values**: Always shows most recent data

### 5. AI Integration
- **MCP Server**: 7 tools accessible to LLMs and AI agents
- **Machine-readable Data**: All data available in JSON format
- **Programmatic Access**: Full API for automation

---

## 🚀 Quick Start with Docker

### Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)
- At least 2GB RAM available

### Installation & Running

1. **Clone the repository**
   ```bash
   cd /home/raul/reps/testes/yipitdata
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Verify services are running**
   ```bash
   docker-compose ps
   ```

   Expected output:
   ```
   NAME                 STATUS
   yipitdata-db         Up (healthy)
   yipitdata-backend    Up (healthy)
   yipitdata-frontend   Up
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs (Swagger UI)
   - Health Check: http://localhost:8000/health

5. **Stop services**
   ```bash
   docker-compose down
   ```

### Troubleshooting

**Services not starting:**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild containers
docker-compose up -d --build
```

**Database connection errors:**
```bash
# Restart PostgreSQL
docker-compose restart db
```

**Port conflicts:**
Edit `docker-compose.yml` to change ports:
```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # Change frontend port
  backend:
    ports:
      - "8001:8000"  # Change backend port
```

---

## 📡 API Endpoints

### Base URL
```
http://localhost:8000
```

### 1. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### 2. Company Search
```
GET /companies
```

**Query Parameters:**
- `query` (optional): Search by ticker or company name
- `sector` (optional): Filter by sector

**Example:**
```bash
curl "http://localhost:8000/companies?query=ACME&sector=E-commerce"
```

**Response:**
```json
{
  "companies": [
    {
      "ticker": "ACME",
      "company_name": "Acme E-commerce",
      "sector": "E-commerce"
    }
  ]
}
```

### 3. Get Company KPIs
```
GET /companies/{ticker}/kpis
```

**Path Parameters:**
- `ticker`: Company ticker symbol (e.g., ACME)

**Example:**
```bash
curl "http://localhost:8000/companies/ACME/kpis"
```

**Response:**
```json
{
  "ticker": "ACME",
  "company_name": "Acme E-commerce",
  "sector": "E-commerce",
  "kpis": [
    {
      "kpi_name": "Total Revenue ($MM)",
      "unit": "$MM"
    },
    {
      "kpi_name": "U.S. Net Added Subscribers",
      "unit": "subs"
    }
  ]
}
```

### 4. Get KPI History
```
GET /kpi/history
```

**Query Parameters:**
- `ticker` (required): Company ticker
- `kpi_name` (required): KPI name
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `is_qtd` (optional): Get QTD data (default: false)

**Example:**
```bash
curl "http://localhost:8000/kpi/history?ticker=ACME&kpi_name=Total%20Revenue%20(%24MM)&start_date=2024-01-01"
```

**Response:**
```json
{
  "kpi_name": "Total Revenue ($MM)",
  "unit": "$MM",
  "ticker": "ACME",
  "data": [
    {
      "period_end": "2025-03-31",
      "fiscal_quarter": "Q1",
      "value": 1050.5,
      "is_qtd": false,
      "as_of_date": null
    }
  ]
}
```

### 5. Get KPI Summary
```
GET /kpi/summary
```

**Query Parameters:**
- `ticker` (required): Company ticker
- `kpi_name` (required): KPI name

**Example:**
```bash
curl "http://localhost:8000/kpi/summary?ticker=ACME&kpi_name=Total%20Revenue%20(%24MM)"
```

**Response:**
```json
{
  "kpi": "Total Revenue ($MM)",
  "unit": "$MM",
  "latest_quarter": {
    "period_end": "2025-12-31",
    "fiscal_quarter": "Q4",
    "value": 1508.28
  },
  "previous_quarter": {
    "period_end": "2025-09-30",
    "fiscal_quarter": "Q3",
    "value": 1052.15
  },
  "qoq_change_pct": 43.35,
  "latest_qtd": {
    "period_end": "2025-12-31",
    "fiscal_quarter": "Q4",
    "value": 1485.2
  },
  "qtd_vs_last_quarter_pct": 41.22,
  "trend": "up"
}
```

### 6. Compare Companies KPI
```
GET /kpi/compare
```

**Query Parameters:**
- `tickers` (required): Comma-separated ticker symbols
- `kpi_name` (required): KPI name to compare

**Example:**
```bash
curl "http://localhost:8000/kpi/compare?tickers=ACME,BUZZ,STRM&kpi_name=Total%20Revenue%20(%24MM)"
```

**Response:**
```json
{
  "kpi_name": "Total Revenue ($MM)",
  "unit": "$MM",
  "data": [
    {
      "ticker": "ACME",
      "company_name": "Acme E-commerce",
      "latest_value": 1508.28,
      "latest_date": "2025-12-31"
    },
    {
      "ticker": "BUZZ",
      "company_name": "BuzzSocial Media",
      "latest_value": 351.89,
      "latest_date": "2025-12-31"
    }
  ]
}
```

### 7. Get Available KPI Names
```
GET /kpi/names
```

**Example:**
```bash
curl "http://localhost:8000/kpi/names"
```

**Response:**
```json
[
  "ASP ($)",
  "Global Net Added Subscribers",
  "Total Revenue ($MM)",
  "U.S. Net Added Subscribers",
  "Units Sold"
]
```

### 8. Reload Data (Admin)
```
POST /admin/reload-data
```

**Query Parameters:**
- `csv_path` (optional): Path to CSV file (default: /app/data/kpi_sample_2000.csv)

**Example:**
```bash
curl -X POST "http://localhost:8000/admin/reload-data"
```

**Response:**
```json
{
  "message": "Data reloaded successfully"
}
```

### Swagger UI

Interactive API documentation available at:
```
http://localhost:8000/docs
```

Provides:
- Full endpoint documentation
- Request/response schemas
- Try-it-out functionality
- Automatic request generation

---

## 🤖 MCP Server Integration

### Overview

The MCP (Model Context Protocol) Server exposes all KPI data operations as tools that LLMs and AI agents can invoke. This enables:

- **AI-powered analytics**: Let LLMs query KPI data
- **Automated reporting**: Generate insights programmatically
- **Agent integration**: Use with AI agents for autonomous analysis
- **Custom workflows**: Build on top of the provided tools

### Available Tools (7 Total)

#### 1. search_companies
Search for companies by name/ticker or filter by sector.

**Inputs:**
- `query` (string, optional): Search term
- `sector` (string, optional): Sector filter

**Output:** List of matching companies

#### 2. get_company_kpis
Get all available KPIs for a specific company.

**Inputs:**
- `ticker` (string, required): Company ticker

**Output:** Company info with list of available KPIs

#### 3. get_kpi_history
Get historical or QTD data for a KPI.

**Inputs:**
- `ticker` (string, required)
- `kpi_name` (string, required)
- `start_date` (string, optional): YYYY-MM-DD format
- `end_date` (string, optional): YYYY-MM-DD format
- `is_qtd` (boolean, optional): Get QTD data

**Output:** Time-series KPI data

#### 4. get_kpi_summary
Get comprehensive KPI insights with QoQ change and trend.

**Inputs:**
- `ticker` (string, required)
- `kpi_name` (string, required)

**Output:** 
- Latest quarter value
- Previous quarter value
- QoQ change percentage
- Trend indicator (up/down/flat)
- QTD comparison data

#### 5. compare_companies_kpi
Compare a KPI across multiple companies.

**Inputs:**
- `tickers` (string, required): Comma-separated list
- `kpi_name` (string, required)

**Output:** Comparative data for all companies

#### 6. list_sectors
Get all available sectors in the database.

**Output:** List of unique sectors

#### 7. list_kpi_names
Get all available KPI names in the database.

**Output:** List of KPI names (5 total)

### Using the MCP Server

The MCP server is built into the backend and automatically starts with the FastAPI application. To use it programmatically:

```python
from app.mcp_server import server, call_tool_handler
import asyncio

async def query_kpi():
    result = await call_tool_handler("get_kpi_summary", {
        "ticker": "ACME",
        "kpi_name": "Total Revenue ($MM)"
    })
    print(result[0].text)

asyncio.run(query_kpi())
```

### Integration Examples

**With Claude/OpenAI:**
Configure the MCP server endpoint in your LLM settings, and the model will automatically have access to all tools.

**With Custom Agents:**
```python
from app.mcp_server import call_tool_handler

# Query data for analysis
data = await call_tool_handler("compare_companies_kpi", {
    "tickers": "ACME,BUZZ,STRM",
    "kpi_name": "Total Revenue ($MM)"
})
```

---

## 🎯 Design Decisions & Trade-offs

### 1. PostgreSQL vs SQLite

**Decision:** PostgreSQL

**Rationale:**
- Better scalability for future growth
- ACID compliance guarantees data integrity
- Supports complex queries and indexing
- Production-ready for enterprise use

**Trade-off:**
- Slightly higher infrastructure complexity
- Docker dependency required

### 2. Denormalized Schema

**Decision:** Single `kpi_data` table with all columns

**Rationale:**
- Faster query performance (no joins needed)
- Simpler application logic
- Easier to load CSV data
- Single index strategy

**Trade-off:**
- Minor data redundancy (company_name, sector repeated)
- Not normalized to 3NF, but acceptable for analytical use case

### 3. Historical + QTD in Same Table

**Decision:** Single table with `is_qtd` boolean flag

**Rationale:**
- Simpler schema management
- Single indexing strategy
- Easy to query either data type

**Trade-off:**
- Could separate into two tables for absolute normalization
- Current approach is pragmatic for the use case

### 4. Async FastAPI

**Decision:** Full async implementation with `async def` endpoints

**Rationale:**
- High concurrency support
- Non-blocking I/O operations
- Better resource utilization
- Modern Python best practice

**Trade-off:**
- Requires understanding of async/await patterns
- All database operations must be compatible

### 5. React Frontend

**Decision:** Client-side React with server-side API

**Rationale:**
- Rich interactive UI
- Real-time filtering and search
- Responsive design for all devices
- Decoupled frontend from backend

**Trade-off:**
- JavaScript in browser (vs server-rendered)
- More client-side state management

### 6. MCP Server Integration

**Decision:** Built into FastAPI backend (not separate service)

**Rationale:**
- Shared database connections
- Simplified deployment
- Single Docker container for backend logic
- Leverages existing API business logic

**Trade-off:**
- Backend handles both REST API and MCP protocol
- Could separate for independent scaling

### 7. Docker Composition

**Decision:** Three separate containers (DB, Backend, Frontend)

**Rationale:**
- Better isolation and scaling
- Independent versioning
- Clear separation of concerns
- Production-like architecture

**Trade-off:**
- More complex local development
- More services to manage

---

## 📊 Observability

### Health Checks

**Backend health check:**
```bash
curl http://localhost:8000/health
```

**Docker health status:**
```bash
docker-compose ps
```

Shows health status for each service (Healthy/Unhealthy)

### Logging

**Backend logs:**
```bash
docker-compose logs backend -f
```

**Frontend logs:**
```bash
docker-compose logs frontend -f
```

**Database logs:**
```bash
docker-compose logs db -f
```

**View all services:**
```bash
docker-compose logs -f
```

### Key Metrics to Monitor

#### Backend (FastAPI)

**Request metrics:**
- Request latency (via uvicorn logs)
- Error rates (500, 404 responses)
- Concurrent connections

**Database metrics:**
- Query execution time
- Connection pool utilization
- Index hit ratios

**Example log entry:**
```
INFO:     127.0.0.1:56234 - "GET /companies?query=ACME HTTP/1.1" 200 OK
INFO:     127.0.0.1:56235 - "GET /kpi/summary?ticker=ACME&kpi_name=Total%20Revenue HTTP/1.1" 200 OK
```

#### Database (PostgreSQL)

**Important metrics:**
- Connection count: `docker-compose exec db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"`
- Index usage: Check slow query logs
- Data growth: Monitor disk usage

#### Frontend (React)

**Key indicators:**
- Page load time
- Bundle size (check browser DevTools)
- JavaScript errors (browser console)
- API call latency (Network tab)

### Performance Monitoring

**Query execution time:**
```bash
docker-compose exec db psql -U postgres -c "\timing" 
```

**Current connections:**
```bash
docker-compose exec db psql -U postgres -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

### Debugging

**Backend debug mode:**
Edit `run_server.py` to set `reload=True` for development:
```python
uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

**Database inspection:**
```bash
# Connect to database
docker-compose exec db psql -U postgres yipitdata

# View table structure
\d kpi_data

# Check table size
SELECT pg_size_pretty(pg_total_relation_size('kpi_data'));

# View indexes
\di
```

**API endpoint testing:**
Use Swagger UI at `http://localhost:8000/docs` or:
```bash
# Test search
curl "http://localhost:8000/companies?query=ACME"

# Test KPI summary
curl "http://localhost:8000/kpi/summary?ticker=ACME&kpi_name=Total%20Revenue%20(%24MM)"

# View all available KPIs
curl "http://localhost:8000/kpi/names"
```

### Performance Optimization Tips

1. **Add caching** for frequently queried companies/KPIs
2. **Implement pagination** for large result sets
3. **Monitor database slow query log** for missing indexes
4. **Profile frontend** bundle size and rendering performance
5. **Use CDN** for static assets in production
6. **Enable query result caching** with Redis

---

## 📝 Data Format Reference

### KPI Value Interpretation

- **$MM**: Values in millions of dollars
- **subs**: Subscription count
- **%**: Percentage values
- **units**: Item count

### Date Formats

- **period_end**: YYYY-MM-DD (last day of fiscal quarter)
- **as_of_date**: YYYY-MM-DD (when QTD estimate was generated)

### Trend Indicators

- **"up"**: QoQ change > 0.5%
- **"down"**: QoQ change < -0.5%
- **"flat"**: QoQ change between -0.5% and 0.5%
- **null**: No previous quarter data available

---

## 📚 Additional Resources

- **API Swagger UI**: http://localhost:8000/docs
- **Database**: PostgreSQL 15, accessible at `localhost:5432`
- **Frontend**: React 18 with TypeScript
- **Charting**: Recharts for interactive visualizations

## 🔄 Continuous Improvement

Potential enhancements:

- [ ] Add caching layer (Redis)
- [ ] Implement pagination for large datasets
- [ ] Add more KPI analysis tools (volatility, growth rates)
- [ ] Support for custom date ranges in frontend
- [ ] Export to CSV functionality
- [ ] Multi-user authentication
- [ ] Real-time data updates
- [ ] Advanced charting options (candlestick, OHLC)
