#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install Docker Desktop/Engine first." >&2
  exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose v2 is required." >&2
  exit 1
fi
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo "[1/4] Starting Postgres, Redis and Ollama..."
docker compose up -d postgres redis ollama

echo "[2/4] Pulling local Ollama model..."
./scripts/pull-model.sh

echo "[3/4] Building and starting API, worker and web..."
docker compose up -d --build api worker web

echo "[4/4] Running smoke test..."
./scripts/smoke-test.sh

echo
echo "BuktiSaham is ready:"
echo "  Web:      http://localhost:3000"
echo "  API docs: http://localhost:8000/docs"
echo "  Ollama:   local only at http://localhost:11434"
