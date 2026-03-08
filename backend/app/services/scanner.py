from app.models import ScannerRow
from app.providers.base import MarketDataProvider
from app.services.time_window import is_premarket_window


class ScannerService:
    def __init__(self, provider: MarketDataProvider) -> None:
        self._provider = provider

    async def get_premarket_breakouts(
        self,
        min_change_pct: float,
        min_volume: int,
        limit: int,
    ) -> list[ScannerRow]:
        if not is_premarket_window():
            return []

        rows = await self._provider.fetch_premarket_rows(limit=limit * 3)
        filtered = [
            row
            for row in rows
            if row.premarket_change_pct >= min_change_pct and row.volume >= min_volume
        ]
        filtered.sort(
            key=lambda row: (row.premarket_change_pct, row.volume),
            reverse=True,
        )
        return filtered[:limit]
