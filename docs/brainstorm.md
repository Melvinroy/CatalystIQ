# CatalystIQ Brainstorm

`mermaid
flowchart TD
    A[Market Data + News Feeds] --> B[Ingestion Pipeline]
    B --> C[Event/Catalyst Classifier]
    C --> D[Scoring Engine]
    D --> E[Watchlist + Alerts]
    D --> F[Daily Catalyst Dashboard]
    E --> G[Trader Actions]
    F --> G
`

## Notes

- Replace each node with concrete services as we implement.
- Add data sources, model choices, and alert rules.
