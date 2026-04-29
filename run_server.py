#!/usr/bin/env python3
"""
Main entry point for YipitData application
Runs both FastAPI backend and MCP server (optionally)
"""

import sys
import logging
import argparse
import subprocess
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_fastapi(host: str = "0.0.0.0", port: int = 8000):
    """Run FastAPI backend"""
    logger.info(f"Starting FastAPI backend on {host}:{port}")
    import uvicorn
    from app.main import app
    
    uvicorn.run(app, host=host, port=port)


def run_mcp():
    """Run MCP server"""
    logger.info("Starting MCP server")
    import asyncio
    from app.mcp_server import main
    
    asyncio.run(main())


def main():
    parser = argparse.ArgumentParser(
        description="YipitData KPI Analytics Application"
    )
    parser.add_argument(
        "--mode",
        choices=["fastapi", "mcp", "all"],
        default="fastapi",
        help="Which server(s) to run"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host for FastAPI server"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for FastAPI server"
    )
    
    args = parser.parse_args()
    
    if args.mode == "fastapi":
        run_fastapi(args.host, args.port)
    elif args.mode == "mcp":
        run_mcp()
    elif args.mode == "all":
        # In production, run with separate processes/containers
        # For now, just run FastAPI (MCP runs via stdio)
        logger.info("Running FastAPI backend (MCP available via stdio)")
        run_fastapi(args.host, args.port)


if __name__ == "__main__":
    main()
