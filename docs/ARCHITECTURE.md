# Architecture

```text
Browser / Next.js
       |
       v
FastAPI API ------------------------------+
  |                                       |
  | create task / enqueue                 | local AI review only
  v                                       v
PostgreSQL <--- RQ Worker -----------> Ollama (qwen3:8b default)
                 |
                 +--> YFinanceProvider ----> Yahoo Finance public/unofficial endpoints
                 |
                 +--> deterministic quant engine
                         technicals
                         fundamentals (best effort)
                         scenarios
                         policy action
                         evidence hash
```

## Hard boundaries

- `research_action` is produced only by deterministic policy code.
- Ollama cannot mutate numeric outputs or publication state.
- `FREE_ONLY_MARKET_DATA=true` rejects any provider other than `yfinance`.
- There is no paid fallback path in the MVP.
- Free market-data failure is visible; it is never hidden by switching providers.

## Replaceable seams

The `MarketDataProvider` interface isolates upstream market-data access. A future licensed IDX/vendor provider can implement the same methods and be enabled only after a deliberate configuration/code change.

The `OllamaClient` is local and keyless. A cloud model is intentionally not implemented in this MVP.
