from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.models import ScannerRow
from app.providers.mock import MockMarketDataProvider
from app.storage.supabase_repo import SupabaseSnapshotRepository


class BoundaryProvider(MockMarketDataProvider):
    async def fetch_premarket_rows(self, limit: int) -> list[ScannerRow]:
        now = datetime.now(tz=ZoneInfo("UTC"))
        return [
            ScannerRow(ticker="A", premarket_change_pct=4.0, volume=100000, last_updated_at=now),
            ScannerRow(ticker="B", premarket_change_pct=4.0, volume=99999, last_updated_at=now),
            ScannerRow(ticker="C", premarket_change_pct=3.9, volume=120000, last_updated_at=now),
            ScannerRow(ticker="D", premarket_change_pct=6.0, volume=200000, last_updated_at=now),
        ][:limit]


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr("app.services.scanner.is_premarket_window", lambda: True)
    app.state.provider = BoundaryProvider()
    from app.services.scanner import ScannerService

    app.state.scanner_service = ScannerService(app.state.provider)
    app.state.settings = get_settings()
    app.state.snapshot_repo = SupabaseSnapshotRepository(app.state.settings)
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_validation_rejects_negative_values(client: TestClient) -> None:
    response = client.get("/api/v1/scanner/premarket?min_change_pct=-1")
    assert response.status_code == 422


def test_boundary_filter_and_sort(client: TestClient) -> None:
    response = client.get("/api/v1/scanner/premarket?min_change_pct=4&min_volume=100000")
    assert response.status_code == 200
    payload = response.json()
    assert [row["ticker"] for row in payload] == ["D", "A"]
    assert payload[1]["premarket_change_pct"] == 4.0
    assert payload[1]["volume"] == 100000


def test_outside_premarket_returns_empty(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.scanner.is_premarket_window", lambda: False)
    response = client.get("/api/v1/scanner/premarket")
    assert response.status_code == 200
    assert response.json() == []
