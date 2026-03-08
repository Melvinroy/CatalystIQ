# CatalystIQ

CatalystIQ is a pre-market breakout scanner web app for US equities.

## Stack

- Frontend: React + Vite
- Backend: FastAPI
- Data provider: Polygon (mock-first workflow)
- Database: Supabase (scan snapshots)

## Project Structure

- `frontend/` UI dashboard
- `backend/` API and providers
- `docs/` planning and diagrams

## Local Development

1. Start backend from `backend/`.
2. Start frontend from `frontend/`.
3. Open the frontend URL and tune thresholds (`4%`, `100K`, `30s` default).

## Deploy Targets

- Frontend: Vercel
- Backend: Render
- Database: Supabase
