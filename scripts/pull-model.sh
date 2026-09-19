#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || cp .env.example .env
set -a
# shellcheck disable=SC1091
source .env
set +a
MODEL="${OLLAMA_MODEL:-qwen3:8b}"

echo "Waiting for Ollama..."
for _ in $(seq 1 60); do
  if docker compose exec -T ollama ollama list >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "Pulling ${MODEL} (one-time download unless already cached)..."
docker compose exec -T ollama ollama pull "$MODEL"
