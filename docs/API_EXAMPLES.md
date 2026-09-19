# API examples

## Health

```bash
curl http://localhost:18000/health
```

## Free quote

```bash
curl http://localhost:18000/v1/market/BBRI/quote
```

## Create task

```bash
TASK=$(curl -s -X POST http://localhost:18000/v1/research-tasks \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"TLKM","horizon_days":90,"capital_idr":"100000000"}')
echo "$TASK"
```

## Local Ollama review only

```bash
curl -X POST http://localhost:18000/v1/ai/review \
  -H 'Content-Type: application/json' \
  -d '{"analysis":{"ticker":"BBCA.JK","research_action":"WATCH","scores":{"confidence":62}}}'
```
