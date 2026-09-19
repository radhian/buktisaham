# Task orchestration API examples

Base URL: http://localhost:18000

## Create a task

~~~bash
curl -X POST http://localhost:18000/v1/research-tasks \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "IDX Banking Quality Review",
    "thesis": "Compare large Indonesian banks under one repeatable research mandate.",
    "tickers": ["BBCA", "BBRI", "BMRI"],
    "horizon_days": 90,
    "capital_idr": "100000000",
    "cadence": "manual",
    "analysis_modules": [
      "technical",
      "fundamental",
      "liquidity",
      "scenario",
      "evidence",
      "ai_review"
    ]
  }'
~~~

Legacy clients can still send a single ticker:

~~~json
{"ticker": "BBCA", "horizon_days": 90, "capital_idr": "100000000"}
~~~

## Browse and update tasks

~~~bash
curl http://localhost:18000/v1/research-tasks
curl http://localhost:18000/v1/research-tasks/<TASK_ID>

curl -X PATCH http://localhost:18000/v1/research-tasks/<TASK_ID> \
  -H 'Content-Type: application/json' \
  -d '{"horizon_days": 180, "tickers": ["BBCA", "BBRI", "BMRI", "BBNI"]}'
~~~

Every update creates a new config version and hash.

## Run a task

~~~bash
curl -X POST http://localhost:18000/v1/research-tasks/<TASK_ID>/runs
~~~

The endpoint returns HTTP 202. A task cannot have two active runs at the same time.

## Observe orchestration

~~~bash
curl http://localhost:18000/v1/runs/<RUN_ID>
~~~

Relevant response fields:

~~~json
{
  "status": "RUNNING",
  "stage": "scenario",
  "progress": 62,
  "message": "Building Bear, Base, and Bull scenarios for BBRI.JK",
  "events": []
}
~~~

Terminal states are **COMPLETED**, **PARTIAL**, and **FAILED**.

## Dashboard and history

~~~bash
curl http://localhost:18000/v1/dashboard
curl http://localhost:18000/v1/runs
curl http://localhost:18000/v1/runs?task_id=<TASK_ID>
curl http://localhost:18000/v1/research-tasks/<TASK_ID>/runs
~~~

## Archive a task

~~~bash
curl -X DELETE http://localhost:18000/v1/research-tasks/<TASK_ID>
~~~

An active task run must finish before the task can be archived.
