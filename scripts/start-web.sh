#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DIR="$ROOT/apps/web"

if [ ! -d "$ROOT/node_modules" ]; then
  echo "ERROR: node_modules not found. Run ./scripts/setup-dev.sh or npm install first."
  exit 1
fi

if [ ! -f "$WEB_DIR/.env.local" ]; then
  echo "WARNING: apps/web/.env.local not found. Copy apps/web/.env.example to apps/web/.env.local"
fi

cd "$WEB_DIR"
echo "Starting PlacementOS Web on http://localhost:3000"
exec npm run dev
