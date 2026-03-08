from datetime import datetime
from zoneinfo import ZoneInfo

import httpx

from app.config import Settings
from app.models import ScannerRow
from app.providers.base import MarketDataProvider


class PolygonMarketDataProvider(MarketDataProvider):
    def __init__(self, settings: Settings) -> None:
        if not settings.polygon_api_key:
            raise ValueError("POLYGON_API_KEY is required when data_provider=polygon")
        self._api_key = settings.polygon_api_key
        self._base_url = settings.polygon_base_url.rstrip("/")

    async def fetch_premarket_rows(self, limit: int) -> list[ScannerRow]:
        params = {"apiKey": self._api_key}
        url = f"{self._base_url}/v2/snapshot/locale/us/markets/stocks/gainers"

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()

        rows: list[ScannerRow] = []
        now = datetime.now(tz=ZoneInfo("UTC"))
        for item in payload.get("tickers", []):
            ticker = item.get("ticker")
            if not ticker:
                continue
            change = float(item.get("todaysChangePerc", 0.0))
            day = item.get("day", {}) or {}
            volume = int(day.get("v", 0) or 0)
            rows.append(
                ScannerRow(
                    ticker=ticker,
                    premarket_change_pct=change,
                    volume=volume,
                    last_updated_at=now,
                )
            )
            if len(rows) >= limit:
                break
        return rows
