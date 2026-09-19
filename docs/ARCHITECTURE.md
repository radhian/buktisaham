# BuktiSaham v0.2.0 architecture

## System context

~~~mermaid
flowchart TB
    U[Research user] --> UI[Next.js task workspace]
    UI --> API[FastAPI orchestration API]
    API --> PG[(PostgreSQL)]
    API --> RQ[Redis queue]
    RQ --> W[Research worker]
    W --> Y[yfinance free EOD adapter]
    W --> Q[Deterministic quant and policy engine]
    W --> O[Local Ollama review]
    W --> PG
~~~

## Domain model

~~~mermaid
erDiagram
    RESEARCH_TASK ||--o{ TASK_CONFIG_VERSION : publishes
    RESEARCH_TASK ||--o{ TASK_RUN : executes
    TASK_RUN ||--o{ RUN_EVENT : emits
    TASK_RUN ||--|| RECOMMENDATION_VERSION : publishes
    TASK_RUN ||--o{ EVIDENCE_ITEM : records
~~~

Existing physical task columns remain backward compatible. The richer task contract is stored in **params_json**, while immutable versions are persisted in **task_config_version**.

## Execution sequence

~~~mermaid
sequenceDiagram
    participant UI as Web workspace
    participant API as FastAPI
    participant Q as Redis/RQ
    participant W as Worker
    participant D as Free data
    participant O as Ollama
    UI->>API: Start saved task
    API->>API: Snapshot config version/hash
    API->>Q: Enqueue run
    API-->>UI: 202 QUEUED
    Q->>W: Execute run
    loop Each IDX ticker
        W->>D: EOD history + fundamentals
        W->>W: Scores + scenarios + policy
        W->>O: Explanation-only review
        W->>W: Evidence + hashes
    end
    W->>API: Persist packet and events
    UI->>API: Poll run
    API-->>UI: Progress or terminal packet
~~~

## Reliability decisions

- One task can have only one queued/running execution.
- Each run snapshots the exact config version and hash.
- Events are append-only and expose stage/progress.
- One ticker failure does not erase successful ticker results.
- A mixed outcome publishes as PARTIAL.
- Deterministic calculations remain publishable when Ollama is unavailable.
- Paid provider fallback is absent by design.

## Deployment

Docker Compose runs six services:

1. web
2. api
3. worker
4. postgres
5. redis
6. ollama

The API is internal port 8000 and host port 18000 by default. Only the web and API host mappings are needed for normal local use.

## Future decomposition triggers

Remain a modular monolith until one of these conditions is met:

- independent worker scaling is required for more than 20 concurrent runs;
- licensed data ingestion requires separate network and entitlement controls;
- report generation materially delays research execution;
- multi-user authorization requires a dedicated identity boundary.
