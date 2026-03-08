from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.models import ScannerRow
from app.providers.base import MarketDataProvider


class MockMarketDataProvider(MarketDataProvider):
    async def fetch_premarket_rows(self, limit: int) -> list[ScannerRow]:
        now = datetime.now(tz=ZoneInfo("UTC"))
        sample = [
            ScannerRow(ticker="NVDA", premarket_change_pct=6.8, volume=510000, last_updated_at=now),
            ScannerRow(ticker="SMCI", premarket_change_pct=9.2, volume=830000, last_updated_at=now - timedelta(seconds=4)),
            ScannerRow(ticker="AMD", premarket_change_pct=4.0, volume=100000, last_updated_at=now - timedelta(seconds=8)),
            ScannerRow(ticker="PLTR", premarket_change_pct=3.2, volume=240000, last_updated_at=now - timedelta(seconds=12)),
            ScannerRow(ticker="IONQ", premarket_change_pct=5.5, volume=98000, last_updated_at=now - timedelta(seconds=15)),
            ScannerRow(ticker="TSLA", premarket_change_pct=4.1, volume=420000, last_updated_at=now - timedelta(seconds=17)),
        ]
        return sample[:limit]
