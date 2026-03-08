from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.models import HealthResponse, ScannerRow
from app.providers.base import MarketDataProvider
from app.providers.mock import MockMarketDataProvider
from app.providers.polygon import PolygonMarketDataProvider
from app.services.scanner import ScannerService
from app.storage.supabase_repo import SupabaseSnapshotRepository


def build_provider(settings: Settings) -> MarketDataProvider:
    provider_name = settings.data_provider.lower().strip()
    if provider_name == "polygon":
        return PolygonMarketDataProvider(settings)
    return MockMarketDataProvider()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.provider = build_provider(settings)
    app.state.scanner_service = ScannerService(app.state.provider)
    app.state.snapshot_repo = SupabaseSnapshotRepository(settings)
    yield


app = FastAPI(title="CatalystIQ API", lifespan=lifespan)
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(f"{settings.api_prefix}/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", provider=settings.data_provider)


@app.get(f"{settings.api_prefix}/scanner/premarket", response_model=list[ScannerRow])
async def scan_premarket(
    min_change_pct: float = Query(default=4.0, ge=0.0),
    min_volume: int = Query(default=100000, ge=0),
    limit: int = Query(default=50, ge=1, le=250),
) -> list[ScannerRow]:
    service: ScannerService = app.state.scanner_service
    snapshot_repo: SupabaseSnapshotRepository = app.state.snapshot_repo

    try:
        rows = await service.get_premarket_breakouts(
            min_change_pct=min_change_pct,
            min_volume=min_volume,
            limit=limit,
        )
        try:
            await snapshot_repo.save_scan(rows, min_change_pct, min_volume)
        except Exception:
            pass
        return rows
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
