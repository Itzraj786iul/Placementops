#!/usr/bin/env python3
"""Verify PostgreSQL connectivity using DATABASE_URL from apps/api/.env."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "apps" / "api" / ".env"


def load_database_url() -> str:
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]

    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DATABASE_URL="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")

    return "postgresql://placementos:placementos@localhost:5432/placementos"


def main() -> int:
    database_url = load_database_url()
    print(f"Checking PostgreSQL at {database_url.split('@')[-1]}...")

    try:
        import psycopg2
    except ImportError:
        print("ERROR: psycopg2 is not installed. Run setup-dev first.")
        return 1

    try:
        conn = psycopg2.connect(database_url)
        conn.close()
        print("PostgreSQL connection successful.")
        return 0
    except Exception as exc:
        print("ERROR: Could not connect to PostgreSQL.")
        print(f"  {exc}")
        print()
        print("Make sure PostgreSQL is running locally and DATABASE_URL is correct.")
        print("Example: postgresql://placementos:placementos@localhost:5432/placementos")
        return 1


if __name__ == "__main__":
    sys.exit(main())
