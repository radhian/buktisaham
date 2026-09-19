# Data-source policy - MVP

## Stock data

Current provider: **Yahoo Finance via `yfinance`**.

Why:

- no API key required
- no per-call fee
- Indonesian tickers are commonly represented with the `.JK` suffix
- sufficient for an EOD/delayed research prototype

Important limitations:

- endpoints are unofficial and not guaranteed stable
- rate limiting or upstream changes can break calls
- upstream terms still apply; "free" does not automatically mean unrestricted redistribution/commercial rights
- this repository is not claiming exchange-grade or licensed production completeness

Configuration enforces:

```env
FREE_ONLY_MARKET_DATA=true
MARKET_DATA_PROVIDER=yfinance
```

No paid fallback is present.

## Official evidence

For a production research platform, official filings, IDX/OJK/KSEI/BI material and issuer IR evidence should be ingested separately and reconciled. This codebase currently focuses on the runnable market-data + deterministic-analysis + local-AI skeleton.
