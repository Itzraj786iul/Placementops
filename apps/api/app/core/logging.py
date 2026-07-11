"""Structured JSON logging helpers for PlacementOS API."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

_CONFIGURED = False


def configure_logging() -> None:
    """Idempotent root logger setup for JSON-friendly stdout logs."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))

    root = logging.getLogger()
    if not root.handlers:
        root.addHandler(handler)
    root.setLevel(logging.INFO)

    # Keep noisy libraries quieter unless debugging.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)


def log_json(logger: logging.Logger, level: int, **fields: Any) -> None:
    logger.log(level, json.dumps(fields, default=str, separators=(",", ":")))
