#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT/apps/api"
VENV="$API_DIR/.venv"

if [ ! -d "$VENV" ]; then
  echo "ERROR: Virtual environment not found. Run ./scripts/setup-dev.sh first."
  exit 1
fi

if [ ! -f "$API_DIR/.env" ]; then
  echo "ERROR: apps/api/.env not found. Copy apps/api/.env.example to apps/api/.env"
  exit 1
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"
cd "$API_DIR"

echo "Starting PlacementOS API on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
exec uvicorn main:app --reload --host 0.0.0.0 --port 8000
