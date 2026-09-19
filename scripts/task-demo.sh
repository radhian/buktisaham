#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -n "${API_URL:-}" ]; then
  API="$API_URL"
else
  API_HOST_PORT="$(docker compose port api 8000 2>/dev/null | tail -n 1 | awk -F: '{print $NF}')"
  API="http://localhost:${API_HOST_PORT:-18000}"
fi

task_file="/tmp/buktisaham-demo-task.json"
run_file="/tmp/buktisaham-demo-run.json"

echo "Creating a multi-stock Indonesian research task..."
curl -fsS -X POST "$API/v1/research-tasks" \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "IDX Banking Quality Review",
    "thesis": "Compare large Indonesian banks under one repeatable evidence-based research mandate.",
    "tickers": ["BBCA", "BBRI", "BMRI"],
    "horizon_days": 90,
    "capital_idr": "100000000",
    "cadence": "manual"
  }' > "$task_file"

task_id="$(python3 -c 'import json; print(json.load(open("/tmp/buktisaham-demo-task.json"))["id"])')"
echo "Task created: $task_id"

curl -fsS -X POST "$API/v1/research-tasks/$task_id/runs" > "$run_file"
run_id="$(python3 -c 'import json; print(json.load(open("/tmp/buktisaham-demo-run.json"))["id"])')"
echo "Run queued: $run_id"

for _ in $(seq 1 180); do
  curl -fsS "$API/v1/runs/$run_id" > "$run_file"
  state="$(python3 -c 'import json; d=json.load(open("/tmp/buktisaham-demo-run.json")); print("{}|{}|{}".format(d["status"], d["progress"], d["stage"]))')"
  echo "$state"
  status="${state%%|*}"
  if [ "$status" = "COMPLETED" ] || [ "$status" = "PARTIAL" ]; then
    python3 - <<'PY'
import json
data = json.load(open('/tmp/buktisaham-demo-run.json'))
summary = data['result']['summary']
print('Published task packet:')
print('  completed symbols:', summary['completed_symbols'])
print('  failed symbols:', summary['failed_symbols'])
print('  action counts:', summary['action_counts'])
print('  bundle hash:', data['result']['bundle_hash'])
PY
    exit 0
  fi
  if [ "$status" = "FAILED" ]; then
    python3 -c 'import json; print(json.load(open("/tmp/buktisaham-demo-run.json")).get("error"))' >&2
    exit 1
  fi
  sleep 2
done

echo "Timed out waiting for task run $run_id" >&2
exit 1
