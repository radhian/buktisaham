#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

API="${API_URL:-http://localhost:8000}"

echo "Waiting for API..."
for _ in $(seq 1 60); do
  if curl -fsS "$API/health" >/tmp/buktisaham-health.json 2>/dev/null; then
    break
  fi
  sleep 2
done

python3 - <<'PY'
import json
p='/tmp/buktisaham-health.json'
with open(p) as f: d=json.load(f)
print('health:', d.get('status'))
print('market provider:', d.get('market_data',{}).get('provider'))
print('free only:', d.get('market_data',{}).get('free_only'))
print('ollama:', d.get('ollama',{}).get('status'))
assert d.get('market_data',{}).get('free_only') is True
assert d.get('market_data',{}).get('paid_fallback_enabled') is False
PY

echo "Checking free market-data endpoint (BBCA)..."
if curl -fsS "$API/v1/market/BBCA/quote" >/tmp/buktisaham-quote.json; then
  python3 - <<'PY'
import json
with open('/tmp/buktisaham-quote.json') as f: d=json.load(f)
print('quote:', d['ticker'], d['last_price'], 'via', d['provider'])
assert d['provider'] == 'yfinance'
PY
else
  echo "WARNING: live free-data smoke test failed. Yahoo Finance may be unavailable/rate-limited. Core services are still running." >&2
fi
