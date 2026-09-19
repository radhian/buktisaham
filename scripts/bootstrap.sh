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

WEB_HOST_PORT="$(docker compose port web 3000 2>/dev/null | tail -n 1 | awk -F: '{print $NF}')"
API_HOST_PORT="$(docker compose port api 8000 2>/dev/null | tail -n 1 | awk -F: '{print $NF}')"
OLLAMA_HOST_PORT="$(docker compose port ollama 11434 2>/dev/null | tail -n 1 | awk -F: '{print $NF}')"

echo
echo "BuktiSaham is ready:"
echo "  Web:      http://localhost:${WEB_HOST_PORT:-3000}"
echo "  API docs: http://localhost:${API_HOST_PORT:-18000}/docs"
echo "  Ollama:   local only at http://localhost:${OLLAMA_HOST_PORT:-11434}"
