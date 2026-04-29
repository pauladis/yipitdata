# YipitData KPI Analytics Platform

A full-stack application for exploring quarterly KPI estimates for public companies. Serves data through a web API, MCP server for AI agents, and includes a React frontend.

## Architecture

```
Frontend (React)
    ↓
Backend API (FastAPI)
    ↓
SQLite Database
    ↓
CSV Data (kpi_sample_2000.csv)

MCP Server (FastMCP)
    ↓
Reuses Backend Services
```

## Key Features

- **KPI Data Exploration**: Browse companies, KPIs, and historical/QTD estimates
- **Trend Analysis**: Automatic QoQ (quarter-over-quarter) change calculations and trend detection
- **Multiple Interfaces**:
  - REST API for frontend/tools
  - MCP server for AI agents (Claude, ChatGPT, etc.)
- **Search & Filter**: Find companies by ticker/name, filter by sector
- **Comparison**: Compare KPIs across multiple companies

## Quick Start

### With Docker (Recommended)

```bash
docker-compose up
```

The application will:
1. Build the Python environment
2. Initialize SQLite database
3. Load CSV data
4. Start FastAPI on http://localhost:8000

Visit http://localhost:8000/docs for interactive API documentation.

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Initialize and load data:**
```bash
python3 -c "from app.loader import load_csv_to_db; load_csv_to_db('kpi_sample_2000.csv')"
```

3. **Run FastAPI backend:**
```bash
python3 run_server.py --mode fastapi --port 8000
```

4. **Run MCP server (optional, separate terminal):**
```bash
python3 run_server.py --mode mcp
```

## API Endpoints

All endpoints are available at `http://localhost:8000`

### Company Search
- `GET /companies?query=ACME` - Search companies
- `GET /companies?sector=E-commerce` - Filter by sector
- `GET /companies/{ticker}/kpis` - Get KPIs for a company

### KPI Data
- `GET /kpi/history?ticker=ACME&kpi_name=Total%20Revenue` - Get historical data
- `GET /kpi/qtd?ticker=ACME&kpi_name=Total%20Revenue` - Get latest QTD data
- `GET /kpi/summary?ticker=ACME&kpi_name=Total%20Revenue` - **Core endpoint** with aggregated insights
- `GET /kpi/compare?tickers=ACME,BCORP&kpi_name=Total%20Revenue` - Compare across companies

### Admin
- `POST /admin/reload-data` - Reload CSV data

### Utilities
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger UI)

## MCP Server Integration

The MCP server exposes tools for LLMs to interact with KPI data. Use it in Claude Desktop, Cursor, or similar tools.

### Tools Available

1. **search_companies(query, sector)** - Find companies
2. **get_company_kpis(ticker)** - List KPIs for company
3. **get_kpi_history(ticker, kpi_name, start_date, end_date, is_qtd)** - Get time-series data
4. **get_kpi_summary(ticker, kpi_name)** - Get aggregated insights ⭐
5. **compare_companies_kpi(tickers, kpi_name)** - Compare KPI across companies
6. **list_sectors()** - Get all sectors
7. **list_kpi_names()** - Get all KPI names

### Example LLM Prompts

```
"What's the latest revenue trend for ACME Inc?"
→ Uses get_kpi_summary("ACME", "Total Revenue")

"Compare subscriber counts across ACME, BCORP, and CCORP"
→ Uses compare_companies_kpi("ACME,BCORP,CCORP", "Global Net Added Subscribers")

"Show me revenue history for ACME from Q1 2024 to Q4 2024"
→ Uses get_kpi_history("ACME", "Total Revenue", "2024-01-01", "2024-12-31")
```

## Database Schema

### kpi_data Table

```
id (INTEGER PRIMARY KEY)
ticker (STRING) - Company ticker
company_name (STRING) - Full company name
sector (STRING) - Industry sector
kpi_name (STRING) - KPI metric name
unit (STRING) - Unit of measurement
period_start (DATE) - Quarter start date
period_end (DATE) - Quarter end date
fiscal_quarter (STRING) - e.g., "2024Q1"
value (FLOAT) - Metric value
is_qtd (BOOLEAN) - True for quarter-to-date, false for historical
as_of_date (DATE) - Date snapshot was taken (QTD only)
created_at (DATE) - Record creation date
```

### Indexes

- `idx_lookup(ticker, kpi_name)` - Fast company/KPI lookups
- `idx_time(ticker, kpi_name, period_end)` - Time-series queries
- `idx_qtd(ticker, kpi_name, is_qtd, as_of_date)` - QTD queries
- `idx_company_kpis(ticker, kpi_name, period_end)` - Company KPI listings

## Data Semantics

- **"Latest quarter"**: Maximum `period_end` date for historical data
- **QTD**: Intra-quarter estimates at a point in time, identified by `as_of_date`
- **QoQ Change**: Percentage change between consecutive quarters
- **Trend**: Computed from QoQ change (>0.5% = up, <-0.5% = down, else = flat)

## Design Decisions & Trade-offs

### SQLite vs PostgreSQL
- **Chosen**: SQLite
- **Rationale**: Small dataset, fast setup, sufficient concurrency for read-heavy workload
- **Trade-off**: Limited scalability for very large datasets; acceptable for this use case

### Denormalized Schema
- **Chosen**: Single table with repeated company/sector info
- **Rationale**: Faster queries, simpler ingestion, minimal overhead
- **Trade-off**: Data duplication; not ideal for updates but acceptable for analytics

### No Caching
- **Rationale**: Dataset is small, SQLite queries are fast (< 50ms)
- **Future**: Add Redis caching if latency becomes an issue

### No RAG/Advanced NLP
- **Rationale**: Unnecessary for structured KPI queries
- **Focus**: Simple, composable MCP tools that LLMs can naturally use

## Observability

### Logging
- Application logs to console with timestamps
- CSV loader logs data ingestion progress
- Query timing available via logs (optional)

### Future Improvements
- Prometheus metrics (query count, latency)
- Distributed tracing (OpenTelemetry)
- Query performance monitoring

## Testing

To verify the setup:

```bash
# Test health
curl http://localhost:8000/health

# Search companies
curl "http://localhost:8000/companies?query=ACME"

# Get KPI summary
curl "http://localhost:8000/kpi/summary?ticker=ACME&kpi_name=Total%20Revenue"
```

## Future Improvements

1. **Database**: Migrate to PostgreSQL for better scalability
2. **Schema**: Normalize with separate company/KPI tables if needed
3. **Caching**: Add Redis for frequently accessed summaries
4. **Search**: Implement Elasticsearch for better company/KPI discovery
5. **Frontend**: Build interactive React dashboard with charts
6. **Authentication**: Add JWT-based auth for private deployments
7. **API Versioning**: Implement v1, v2 endpoints for backward compatibility
8. **Webhooks**: Notify clients when new KPI data arrives
9. **Batch Exports**: Export data to CSV/Excel for offline analysis
10. **Analytics**: Track most-viewed KPIs and popular queries

## Development

### Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── database.py       # SQLAlchemy models & setup
│   ├── schemas.py        # Pydantic models
│   ├── services.py       # Business logic
│   ├── loader.py         # CSV loader
│   └── mcp_server.py     # MCP server definition
├── data/
│   └── kpi_sample_2000.csv
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run_server.py         # Server entry point
└── README.md
```

### Linting & Type Checking

```bash
# Type checking (when available)
mypy app/

# Format code
black app/ run_server.py

# Lint
flake8 app/ run_server.py
```

## Troubleshooting

**Q: Database not initialized on startup**
A: Check CSV path in environment variables (`CSV_PATH` env var) or pass it explicitly

**Q: MCP server not responding**
A: MCP uses stdio protocol; ensure it's run as a subprocess with proper I/O setup

**Q: Slow queries**
A: Check database indexes are created; run `/admin/reload-data` to reinitialize

## License

MIT
