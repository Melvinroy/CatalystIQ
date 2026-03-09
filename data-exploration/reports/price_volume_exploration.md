# Price/Volume Exploration Report

## Context

- Date:
- Analyst:
- Providers tested: Polygon, Finnhub
- Universe: Top movers
- Lookback: Last 2 trading days + live snapshots

## Field Catalog and Coverage

| field | polygon coverage | finnhub coverage | notes |
|---|---:|---:|---|
| symbol | | | |
| ts_utc | | | |
| last_price | | | |
| change_pct | | | |
| volume | | | |
| prev_close | | | |

## Data Quality Summary

### Null Rates

| field | null_rate |
|---|---:|

### Duplicates

- Duplicate rows on (`provider`, `symbol`, `ts_utc`, `source_endpoint`): 

### Outliers

- Invalid/non-positive prices:
- Negative volumes:

## Provider Parity

- Overlap symbols:
- Price drift stats:
- Change % drift stats:
- Volume comparability notes:

## Threshold Recommendations

- Suggested `min_change_pct`:
- Suggested `min_volume`:
- Session-specific threshold adjustments:

## Recommendation (Go/No-Go)

- Primary provider for V1 runtime:
- Backup provider strategy:
- Key risks:
