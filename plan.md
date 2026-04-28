# KPI Analytics Platform – Implementation Plan

## 🎯 Objective

Build a full-stack application that allows users (humans + AI agents) to:
- Explore companies and KPIs
- Visualize historical and QTD (Quarter-To-Date) data
- Quickly understand performance trends

The system must expose:
- A web frontend (React)
- A backend API (FastAPI)
- An MCP server (for LLM/AI consumption)

---

## 🧠 Key Design Principles

- Prioritize **simplicity over over-engineering**
- Optimize for **read performance (analytics use case)**
- Design for **LLM usability (via MCP tools)**
- Keep system **deterministic and predictable**
- Avoid unnecessary complexity (e.g., no RAG)

---

## 🏗️ High-Level Architecture


Frontend (React)
↓
Backend API (FastAPI)
↓
SQLite (loaded from CSV)

MCP Server (FastMCP)
↑
Reuses Backend API


---

## 📦 Data Source

- Initial dataset: CSV file (`kpi_sample_2000.csv`)
- Assumption: Data is already clean and processed
- Load strategy:
  - Load CSV into SQLite on startup
  - Replace table on each load (idempotent)

---

## 🗄️ Database Design (SQLite)

### Table: `kpi_data`

Denormalized for simplicity and performance.

```sql
kpi_data (
  id INTEGER PRIMARY KEY AUTOINCREMENT,

  ticker TEXT NOT NULL,
  company_name TEXT,
  sector TEXT,

  kpi_name TEXT NOT NULL,
  unit TEXT,

  period_end DATE,
  fiscal_quarter TEXT,

  value REAL NOT NULL,

  is_qtd BOOLEAN DEFAULT 0,
  as_of_date DATE
)
Rationale

Pros

Simple ingestion (1:1 with CSV)
Faster queries (no joins)
Faster development

Cons

Data duplication
Less scalable long-term
⚡ Indexing Strategy
CREATE INDEX idx_lookup 
ON kpi_data (ticker, kpi_name);

CREATE INDEX idx_time 
ON kpi_data (ticker, kpi_name, period_end);

CREATE INDEX idx_qtd 
ON kpi_data (ticker, kpi_name, is_qtd, as_of_date);
🔌 Backend API (FastAPI)
Endpoints
GET /companies?query=
GET /companies/{ticker}/kpis
GET /kpi/history
GET /kpi/qtd
GET /kpi/summary ⭐ (core endpoint)
📊 Core Feature: get_kpi_summary
Responsibilities
Fetch latest historical quarter
Fetch previous quarter
Compute QoQ % change
Fetch latest QTD
Compare QTD vs last quarter
Provide auto-highlight trend
Output Shape (standardized)
{
  "kpi": "Total Revenue",
  "unit": "USD",
  "latest_quarter": {...},
  "previous_quarter": {...},
  "qoq_change_pct": 5.2,
  "latest_qtd": {...},
  "qtd_vs_last_quarter_pct": 3.1,
  "trend": "up"
}
Edge Cases
No previous quarter → return null
No QTD → return null
Previous value = 0 → avoid division errors
Multiple QTD → use latest (as_of_date)
Non-sequential quarters → rely on ordering
🤖 MCP Server (FastMCP)
Goal

Expose structured tools for LLMs to interact with KPI data efficiently.

Tools
1. search_companies(query, sector)
Find companies by name/ticker
2. get_company_kpis(ticker)
List available KPIs
3. get_kpi_history(ticker, kpi_name, start_date, end_date)
Time-series data
4. get_kpi_summary(ticker, kpi_name) ⭐
Aggregated insights (most important tool)
5. compare_companies_kpi(tickers, kpi_name)
Compare KPI across multiple companies
🧠 MCP Design Principles
Small, composable tools
Avoid raw data dumps
Return structured, consistent outputs
Reduce LLM reasoning burden (precompute insights)

🎨 Frontend (React)
Required Features
Search companies
Select KPI
Display chart:
Historical data
QTD overlay
Filter by date range
Show “last updated” timestamp
Notes
Keep UI minimal (not focus of evaluation)
Use chart library (e.g., Recharts)
📉 Data Semantics
“Latest quarter” = max period_end
QTD is:
Intra-quarter estimate
Compared directionally (not exact match)
⚖️ Trade-offs
SQLite vs Postgres

SQLite

Pros: simple, fast setup, sufficient for small data
Cons: limited scalability, concurrency
Denormalized Schema

Pros

Faster development
Better read performance

Cons

Redundant data
Not ideal for large-scale systems
No Caching

Reason

Dataset is small
SQLite queries are fast
Avoid premature optimization
🧪 Failure Handling

System should gracefully handle:

Invalid ticker → empty response
Missing KPI → empty response
No historical data → empty array
Missing QTD → null fields
🐳 Docker Setup

Single container:

FastAPI backend
MCP server
SQLite DB

Run via:

docker-compose up
🔍 Observability

Minimal:

Request logging
Query timing logs

Future:

Metrics (latency, usage)
Tracing
🚀 Future Improvements
Move to Postgres
Normalize schema
Add materialized views for summaries
Add caching layer (Redis)
Improve search (ElasticSearch)
Add authentication
🧭 Implementation Order
CSV → SQLite loader
Backend API
get_kpi_summary logic
MCP server
Frontend
Docker + README
🧠 Final Notes

This system is optimized for:

Simplicity
Fast iteration
Clear LLM interaction

Avoid:

Over-engineering
Feature creep
Unnecessary abstractions


