#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[1/8] Python syntax"
python3 -m compileall -q backend/app

echo "[2/8] Required files"
for f in docker-compose.yml .env.example README.md backend/app/main.py frontend/app/page.tsx frontend/lib/i18n.ts frontend/package-lock.json scripts/bootstrap.sh scripts/task-demo.sh; do
  test -f "$f" || { echo "Missing $f" >&2; exit 1; }
done

echo "[3/8] Free-only guard present"
grep -q 'FREE_ONLY_MARKET_DATA=true' .env.example
grep -q 'MARKET_DATA_PROVIDER=yfinance' .env.example
grep -q 'paid_fallback_enabled.*False' backend/app/services/analysis_engine.py

echo "[4/8] Local Ollama guard present"
grep -q 'OLLAMA_MODEL=qwen3:8b' .env.example
grep -q '/api/chat' backend/app/services/ollama_client.py

echo "[5/8] Configurable host ports present"
grep -q 'API_HOST_PORT=18000' .env.example
grep -q '\${API_HOST_PORT:-18000}:8000' docker-compose.yml
grep -q 'NEXT_PUBLIC_API_BASE_URL=http://localhost:18000' .env.example

echo "[6/8] Task orchestration contract present"
grep -q 'class TaskConfigVersion' backend/app/models.py
grep -q 'class RunEvent' backend/app/models.py
grep -q 'product_mode.*TASK_ORCHESTRATION' backend/app/worker_jobs.py
grep -q '/v1/dashboard' frontend/lib/api.ts

echo "[7/8] Localization contract present"
grep -q "buktisaham-language" frontend/app/page.tsx
grep -q "Bahasa Indonesia" frontend/lib/i18n.ts
grep -q "flowchart TB" README.md

echo "[8/8] Patched frontend dependencies present"
grep -q '"next": "15.5.24"' frontend/package.json
grep -q '"react": "19.1.5"' frontend/package.json

echo "Package structure verification passed."
