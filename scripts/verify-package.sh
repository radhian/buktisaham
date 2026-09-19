#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/5] Python syntax"
python3 -m compileall -q backend/app

echo "[2/5] Required files"
for f in docker-compose.yml .env.example README.md backend/app/main.py frontend/app/page.tsx scripts/bootstrap.sh; do
  test -f "$f" || { echo "Missing $f" >&2; exit 1; }
done

echo "[3/5] Free-only guard present"
grep -q 'FREE_ONLY_MARKET_DATA=true' .env.example
grep -q 'MARKET_DATA_PROVIDER=yfinance' .env.example
grep -q 'paid_fallback_enabled.*False' backend/app/services/analysis_engine.py

echo "[4/5] Local Ollama guard present"
grep -q 'OLLAMA_MODEL=qwen3:8b' .env.example
grep -q '/api/chat' backend/app/services/ollama_client.py

echo "[5/5] Configurable host ports present"
grep -q 'API_HOST_PORT=18000' .env.example
grep -q '\${API_HOST_PORT:-18000}:8000' docker-compose.yml
grep -q 'NEXT_PUBLIC_API_BASE_URL=http://localhost:18000' .env.example

echo "Package structure verification passed."
