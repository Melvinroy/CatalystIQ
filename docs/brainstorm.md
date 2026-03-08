# CatalystIQ Brainstorm

```mermaid
flowchart TD
    A[Market Data + News Feeds] --> B[Ingestion Pipeline]
    B --> C[Event/Catalyst Classifier]
    C --> D[Scoring Engine]
    D --> E[Watchlist + Alerts]
    D --> F[Daily Catalyst Dashboard]
    E --> G[Trader Actions]
    F --> G
```

## Notes

- Component A in V1: pre-market breakout scanner.
- Component B: placeholder panel for future expansion.
