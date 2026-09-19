# Task orchestration contract

## Task

A task is a reusable research mandate, not a completed recommendation.

Required business meaning:

- **name** identifies the mandate;
- **thesis** explains what decision the task supports;
- **tickers** define the IDX research universe;
- **horizon_days** controls scenario horizon;
- **capital_idr** provides a decision context, not a brokerage balance;
- **analysis_modules** declares the expected pipeline;
- **cadence** is metadata in v0.2.1 and does not yet trigger automatic runs.

## Configuration version

Every create or update publishes an immutable configuration row:

~~~text
task_id
version
config_hash
config_json
created_at
~~~

A run stores the selected version, hash, and full config as its snapshot.

## Run

A run is one asynchronous execution of one task snapshot.

Invariants:

- only one active run per task;
- status transitions are explicit;
- successful outputs are immutable;
- events are append-only;
- partial success is published;
- no provider silently falls back to a paid source.

## Progress

Local ticker progress is mapped into aggregate task progress so a multi-stock task still reports one monotonically increasing percentage.

## Result packet

~~~json
{
  "schema_version": "2.0",
  "product_mode": "TASK_ORCHESTRATION",
  "task": {},
  "config_snapshot": {},
  "summary": {
    "requested_symbols": 3,
    "completed_symbols": 3,
    "failed_symbols": 0,
    "action_counts": {},
    "average_confidence": 78.4
  },
  "analyses": [],
  "errors": [],
  "primary_analysis": {},
  "bundle_hash": "sha256:..."
}
~~~

## AI authority

Ollama consumes the deterministic packet and returns narrative fields only. The worker does not read an AI-proposed action and does not permit the model to overwrite:

- source facts;
- market prices;
- score values;
- scenario probabilities or prices;
- policy reasons;
- research action;
- evidence hashes.
