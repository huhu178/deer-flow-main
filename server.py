import os
from dotenv import load_dotenv

# --- 调试代码开始 ---
print(f"Attempting to load .env file. Current PWD for server.py: {os.getcwd()}")
# 尝试从当前工作目录或其父目录加载 .env
# 通常，如果 .env 在项目根目录，而 server.py 在项目根目录运行，则不需要指定路径
loaded = load_dotenv() 
print(f".env file loaded status: {loaded}")
retrieved_key = os.getenv('SERPAPI_API_KEY')
if retrieved_key:
    print(f"SERPAPI_API_KEY successfully retrieved from environment: YES (length: {len(retrieved_key)})")
else:
    print("SERPAPI_API_KEY NOT FOUND in environment after load_dotenv()")
# --- 调试代码结束 ---

# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Server script for running the DeerFlow API.
"""

import argparse
import logging

import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the DeerFlow API server")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (default: True except on Windows)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind the server to (default: localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Log level (default: info)",
    )

    args = parser.parse_args()

    # Determine reload setting
    reload = False

    # Command line arguments override defaults
    if args.reload:
        reload = True

    logger.info("Starting DeerFlow API server")
    uvicorn.run(
        "src.server:app",
        host=args.host,
        port=args.port,
        reload=reload,
        log_level=args.log_level,
    )
