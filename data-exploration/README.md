# Data Exploration (Phase 0)

This workspace explores market data quality before deeper backend feature work.

## Goals

- Profile Polygon data first for price/volume scanner suitability.
- Run Finnhub parity checks on overlap symbols.
- Produce normalized parquet datasets and a findings report.

## Structure

- `notebooks/` exploration notebooks
- `data/raw/` raw API pulls
- `data/processed/` normalized parquet outputs
- `reports/` analysis summaries and recommendations
- `config/` workflow configuration
- `schema/` normalized data contract
- `src/` reusable helper functions for notebooks

## Quick Start

1. Copy `.env.example` to `.env` and set API keys.
2. Create a virtual environment and install requirements.
3. Open Jupyter and run notebooks in order.

### Windows commands

```powershell
cd data-exploration
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
jupyter lab
```

## Notebook Order

1. `01_polygon_snapshot_profile.ipynb`
2. `02_polygon_2day_intraday_profile.ipynb`
3. `03_finnhub_parity_check.ipynb`
4. `04_scanner_threshold_recommendations.ipynb`

## Output Expectations

- Raw pulls in `data/raw/`
- Cleaned normalized parquet in `data/processed/`
- Final report in `reports/price_volume_exploration.md`
