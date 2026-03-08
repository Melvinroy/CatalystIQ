from datetime import datetime
from zoneinfo import ZoneInfo

from app.models import ScannerRow
from app.providers.base import MarketDataProvider
from app.services.scanner import ScannerService


class FakeProvider(MarketDataProvider):
    async def fetch_premarket_rows(self, limit: int) -> list[ScannerRow]:
        now = datetime.now(tz=ZoneInfo("UTC"))
        return [
            ScannerRow(ticker="X", premarket_change_pct=8.0, volume=110000, last_updated_at=now),
            ScannerRow(ticker="Y", premarket_change_pct=8.0, volume=90000, last_updated_at=now),
            ScannerRow(ticker="Z", premarket_change_pct=5.0, volume=200000, last_updated_at=now),
        ]


async def test_scanner_service_filters_and_sorts(monkeypatch) -> None:
    monkeypatch.setattr("app.services.scanner.is_premarket_window", lambda: True)
    svc = ScannerService(FakeProvider())
    rows = await svc.get_premarket_breakouts(min_change_pct=4.0, min_volume=100000, limit=10)
    assert [r.ticker for r in rows] == ["X", "Z"]


async def test_scanner_service_outside_session(monkeypatch) -> None:
    monkeypatch.setattr("app.services.scanner.is_premarket_window", lambda: False)
    svc = ScannerService(FakeProvider())
    rows = await svc.get_premarket_breakouts(min_change_pct=0.0, min_volume=0, limit=10)
    assert rows == []
