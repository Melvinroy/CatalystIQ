# Normalized Dataset Contract

This contract defines scanner-ready records emitted from exploration notebooks.

## Required Columns

| column | type | nullable | description |
|---|---|---|---|
| provider | string | no | `polygon` or `finnhub` |
| symbol | string | no | stock ticker |
| ts_utc | datetime64[ns, UTC] | no | observation timestamp |
| session | string | no | `premarket` \| `regular` \| `afterhours` |
| last_price | float64 | no | latest traded/close proxy price |
| change_pct | float64 | no | percent move vs previous close |
| volume | int64 | no | current/period volume |
| prev_close | float64 | no | prior close reference |
| source_endpoint | string | no | endpoint used for the record |
| pull_id | string | no | unique identifier for ingestion pull |

## Optional Columns

| column | type | nullable | description |
|---|---|---|---|
| provider_payload | string (JSON) | yes | raw payload slice for debug/schema drift |

## Uniqueness Rule

Deduplicate on (`provider`, `symbol`, `ts_utc`, `source_endpoint`).

## Session Labeling

Session is classified in `America/New_York`:
- premarket: 04:00-09:30
- regular: 09:30-16:00
- afterhours: 16:00-20:00
