"""
MCP Server for YipitData KPI Analytics
Exposes tools for LLMs to interact with KPI data
"""

import json
import logging
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import asyncio

from app.database import SessionLocal, init_db
from app import services

logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Create MCP server
server = Server("yipitdata-kpi-server")


# Define tools metadata
TOOLS = [
    {
        "name": "search_companies",
        "description": "Search for companies by name/ticker or filter by sector.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term (company name or ticker)"
                },
                "sector": {
                    "type": "string",
                    "description": "Filter by sector name"
                }
            }
        }
    },
    {
        "name": "get_company_kpis",
        "description": "Get all available KPIs for a specific company.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Company ticker symbol (e.g., 'AAPL')"
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "get_kpi_history",
        "description": "Get historical or QTD (quarter-to-date) data for a KPI.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Company ticker symbol"
                },
                "kpi_name": {
                    "type": "string",
                    "description": "Name of the KPI"
                },
                "start_date": {
                    "type": "string",
                    "description": "Optional start date (YYYY-MM-DD format)"
                },
                "end_date": {
                    "type": "string",
                    "description": "Optional end date (YYYY-MM-DD format)"
                },
                "is_qtd": {
                    "type": "boolean",
                    "description": "If true, return QTD data; if false, return historical data",
                    "default": False
                }
            },
            "required": ["ticker", "kpi_name"]
        }
    },
    {
        "name": "get_kpi_summary",
        "description": "Get comprehensive KPI summary with insights including latest quarter, QoQ change, and trend.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Company ticker symbol"
                },
                "kpi_name": {
                    "type": "string",
                    "description": "Name of the KPI"
                }
            },
            "required": ["ticker", "kpi_name"]
        }
    },
    {
        "name": "compare_companies_kpi",
        "description": "Compare a KPI across multiple companies.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "string",
                    "description": "Comma-separated list of ticker symbols (e.g., 'AAPL,GOOGL,META')"
                },
                "kpi_name": {
                    "type": "string",
                    "description": "Name of the KPI to compare"
                }
            },
            "required": ["tickers", "kpi_name"]
        }
    },
    {
        "name": "list_sectors",
        "description": "Get a list of all available sectors in the database.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "list_kpi_names",
        "description": "Get a list of all available KPI names in the database.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


@server.list_tools()
async def list_tools_handler() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name=tool["name"],
            description=tool["description"],
            inputSchema=tool["inputSchema"]
        )
        for tool in TOOLS
    ]


@server.call_tool()
async def call_tool_handler(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    db = SessionLocal()
    try:
        if name == "search_companies":
            query = arguments.get("query")
            sector = arguments.get("sector")
            results = services.get_companies(db, query=query, sector=sector)
            return [TextContent(type="text", text=json.dumps(results, default=str))]
        
        elif name == "get_company_kpis":
            ticker = arguments.get("ticker")
            result = services.get_company_kpis(db, ticker)
            if not result:
                return [TextContent(type="text", text=json.dumps({"error": f"Company {ticker} not found"}))]
            return [TextContent(type="text", text=result.model_dump_json())]
        
        elif name == "get_kpi_history":
            from datetime import datetime
            
            ticker = arguments.get("ticker")
            kpi_name = arguments.get("kpi_name")
            start_date_str = arguments.get("start_date")
            end_date_str = arguments.get("end_date")
            is_qtd = arguments.get("is_qtd", False)
            
            start_date = None
            end_date = None
            
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                except ValueError:
                    return [TextContent(type="text", text=json.dumps({"error": "Invalid start_date format. Use YYYY-MM-DD"}))]
            
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                except ValueError:
                    return [TextContent(type="text", text=json.dumps({"error": "Invalid end_date format. Use YYYY-MM-DD"}))]
            
            result = services.get_kpi_history(
                db, ticker, kpi_name,
                start_date=start_date,
                end_date=end_date,
                is_qtd=is_qtd
            )
            if not result:
                return [TextContent(type="text", text=json.dumps({"error": f"No data found for {ticker} {kpi_name}"}))]
            return [TextContent(type="text", text=result.model_dump_json())]
        
        elif name == "get_kpi_summary":
            ticker = arguments.get("ticker")
            kpi_name = arguments.get("kpi_name")
            
            result = services.get_kpi_summary(db, ticker, kpi_name)
            if not result:
                return [TextContent(type="text", text=json.dumps({"error": f"KPI {kpi_name} not found for {ticker}"}))]
            return [TextContent(type="text", text=result.model_dump_json())]
        
        elif name == "compare_companies_kpi":
            tickers_str = arguments.get("tickers")
            kpi_name = arguments.get("kpi_name")
            
            ticker_list = [t.strip().upper() for t in tickers_str.split(",")]
            result = services.compare_companies_kpi(db, ticker_list, kpi_name)
            if not result:
                return [TextContent(type="text", text=json.dumps({"error": f"Comparison data not found for {kpi_name}"}))]
            return [TextContent(type="text", text=result.model_dump_json())]
        
        elif name == "list_sectors":
            from app.database import KPIData
            sectors = db.query(KPIData.sector).distinct().all()
            sector_list = [s[0] for s in sectors if s[0]]
            return [TextContent(type="text", text=json.dumps(sector_list))]
        
        elif name == "list_kpi_names":
            from app.database import KPIData
            kpis = db.query(KPIData.kpi_name).distinct().all()
            kpi_list = [kpi[0] for kpi in kpis if kpi[0]]
            return [TextContent(type="text", text=json.dumps(kpi_list))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    
    finally:
        db.close()


async def main():
    """Run the MCP server."""
    async with server:
        logger.info("YipitData KPI MCP Server started")
        await server.wait_for_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
