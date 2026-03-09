# Notebooks Guide

This folder contains the single end-to-end exploration notebook:

- `00_data_exploration_end_to_end.ipynb`

## Setup

From repo root:

```powershell
cd data-exploration
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and set keys:

- `POLYGON_API_KEY=...`
- `FINNHUB_API_KEY=...` (optional but needed for parity section)

## Run

```powershell
cd data-exploration
.\.venv\Scripts\Activate.ps1
jupyter lab
```

Then open:

- `notebooks/00_data_exploration_end_to_end.ipynb`

Run all cells top to bottom.

## Outputs

- Raw pulls: `../data/raw/`
- Processed parquet: `../data/processed/`
- Findings report template: `../reports/price_volume_exploration.md`

## Notes

- If `FINNHUB_API_KEY` is empty, the notebook skips parity checks and still runs Polygon sections.
- Keep API keys in `.env` only. Do not paste them into the notebook.
