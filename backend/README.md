# CatalystIQ Backend

FastAPI service for the pre-market breakout scanner.

## Run

1. Create a venv and install dependencies.
   - `python -m venv .venv`
   - `.venv\\Scripts\\activate`
   - `pip install -r requirements.txt`
2. Copy `.env.example` to `.env`.
3. Start server.
   - `uvicorn app.main:app --reload --port 8000`

## API

- `GET /api/v1/health`
- `GET /api/v1/scanner/premarket?min_change_pct=4&min_volume=100000&limit=50`

## Providers

- `DATA_PROVIDER=mock` for local UI-first development.
- `DATA_PROVIDER=polygon` to use Polygon live data.

## Supabase

Run `supabase_schema.sql` in your Supabase SQL editor, then set `SUPABASE_URL` and `SUPABASE_KEY`.
