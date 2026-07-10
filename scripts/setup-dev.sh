#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT/apps/api"
VENV="$API_DIR/.venv"

echo "==> PlacementOS native development setup"

command -v node >/dev/null 2>&1 || { echo "ERROR: Node.js is required. Install Node.js 20+."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ERROR: Python 3 is required. Install Python 3.12+."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "ERROR: npm is required."; exit 1; }

echo "==> Installing Node dependencies"
cd "$ROOT"
npm install

echo "==> Setting up Python virtual environment"
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install --upgrade pip
pip install -r "$API_DIR/requirements.txt"
pip install pytest

echo "==> Checking environment files"
if [ ! -f "$API_DIR/.env" ]; then
  cp "$API_DIR/.env.example" "$API_DIR/.env"
  echo "Created apps/api/.env from example — update credentials before running."
fi
if [ ! -f "$ROOT/apps/web/.env.local" ]; then
  cp "$ROOT/apps/web/.env.example" "$ROOT/apps/web/.env.local"
  echo "Created apps/web/.env.local from example."
fi

echo "==> Verifying PostgreSQL connection"
python "$ROOT/scripts/verify-postgres.py" || {
  echo "WARNING: PostgreSQL check failed. Start PostgreSQL and run migrations manually:"
  echo "  cd apps/api && source .venv/bin/activate && alembic upgrade head"
  exit 1
}

echo "==> Running database migrations"
cd "$API_DIR"
alembic upgrade head

echo "==> Seeding development login accounts"
python "$ROOT/scripts/seed-dev-users.py"

echo ""
echo "Setup complete."
echo "  Start API:  ./scripts/start-api.sh"
echo "  Start Web:  ./scripts/start-web.sh"
echo "  Or both:    npm run dev (from repo root)"
