"""
File Name: logging.py
Author: Senthilnathan Karuppaiah
Date: 11-JUL-2026
Description:
The ONE place logging is configured for the whole backend (see
backend/AGENTS.md — no other module may configure logging or print()).

This module provides the shared structured logger by:
1. Creating a ./logs directory next to the working directory.
2. Writing one JSON-lines log file per invocation, named
   <entry_point>_<YYYYmmdd_HHMMSS>.log, plus mirroring to stdout.
3. Configuring structlog (ISO timestamps, level, logger name, JSON
   renderer) exactly once; library modules inherit via
   structlog.get_logger(__name__).

Environment Variables (.env at repo root):
- LOG_LEVEL: minimum level for the run (default: INFO)
"""

# Import necessary libraries
import logging
import os
import sys
from datetime import datetime

import structlog

# Guard so repeated get_logger() calls (tests, api + cli in one process)
# configure handlers exactly once.
_configured = False


def get_logger(script_name: str):
    """Configure logging for an entry point and return the root structlog logger."""
    global _configured
    if not _configured:
        # Create logs directory if it doesn't exist
        os.makedirs("./logs", exist_ok=True)
        # Generate a log filename with the current timestamp
        log_filename = f"./logs/{script_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
        # File + stdout handlers; structlog renders the JSON line, stdlib routes it
        logging.basicConfig(
            level=level,
            format="%(message)s",
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler(sys.stdout),
            ],
        )
        structlog.configure(
            logger_factory=structlog.stdlib.LoggerFactory(),
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
        )
        _configured = True
    return structlog.get_logger(script_name)
