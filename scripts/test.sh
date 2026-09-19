#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "Backend tests..."
if [ -x backend/.venv/bin/python ]; then
  (cd backend && .venv/bin/python -m pytest -q)
elif command -v pytest >/dev/null 2>&1; then
  (cd backend && pytest -q)
else
  echo "No local pytest environment found; running backend tests in Docker..."
  docker compose run --rm api sh -lc 'pip install -q pytest && pytest -q'
fi

echo "Frontend build check..."
if [ -d frontend/node_modules ]; then
  (cd frontend && npm run build)
elif command -v docker >/dev/null 2>&1; then
  docker compose build web
else
  echo "Skipping frontend build: install npm dependencies or Docker." >&2
fi
